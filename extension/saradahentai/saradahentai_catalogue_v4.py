#!/usr/bin/env python3
"""Extracteur public read-only SaradaHentai V4, bibliothèque standard uniquement."""
import argparse, json, re, sys, time, html
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser

VIDEO_EXT = (".mp4", ".webm", ".m4v", ".mov", ".m3u8", ".mpd")

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.videos, self.in_video = {}, [], [], False
        self.anchor = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            k = (a.get("property") or a.get("name") or "").lower()
            if k and a.get("content"): self.meta[k] = a["content"]
        elif tag == "a" and a.get("href"):
            self.anchor = {"href":a["href"],"text":""}
        elif tag == "video":
            self.in_video = True
            if a.get("src"): self.videos.append((a["src"],"video[src]"))
        elif tag == "source" and self.in_video and a.get("src"):
            self.videos.append((a["src"],"source[src]"))
    def handle_data(self, data):
        if self.anchor is not None: self.anchor["text"] += data
    def handle_endtag(self, tag):
        if tag == "a" and self.anchor is not None:
            self.anchor["text"] = " ".join(self.anchor["text"].split())
            self.links.append(self.anchor); self.anchor = None
        if tag == "video": self.in_video = False

def txt(v):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",html.unescape(v or ""))).strip()

def uniq(xs):
    return list(dict.fromkeys(x for x in xs if x))

class Client:
    def __init__(self, base, delay, timeout):
        self.base=base.rstrip("/")+"/"; self.host=(urlparse(self.base).hostname or "").lower()
        self.delay=delay; self.timeout=timeout; self.last=0; self.errors=[]
    def allowed(self,u):
        h=(urlparse(u).hostname or "").lower()
        return h==self.host or h.endswith("."+self.host)
    def get(self,u,limit=6000000):
        if not self.allowed(u):
            self.errors.append({"url":u,"error":"host_not_allowed"}); return None
        wait=self.delay-(time.monotonic()-self.last)
        if wait>0: time.sleep(wait)
        self.last=time.monotonic()
        try:
            req=Request(u,headers={"User-Agent":"SaradaHentaiCatalogue/4.0 (public read-only metadata)","Accept":"application/json,text/html,*/*"})
            with urlopen(req,timeout=self.timeout) as r:
                data=r.read(limit+1)
                if len(data)>limit:
                    self.errors.append({"url":u,"error":"response_limit"}); return None
                return data
        except HTTPError as e:
            self.errors.append({"url":u,"status":e.code,"error":"http_error"})
            e.close()
        except (URLError,TimeoutError,OSError) as e:
            self.errors.append({"url":u,"error":type(e).__name__})
        return None
    def range(self,u,start=0,end=1048575):
        if not self.allowed(u): return None
        wait=self.delay-(time.monotonic()-self.last)
        if wait>0: time.sleep(wait)
        self.last=time.monotonic()
        try:
            req=Request(u,headers={"User-Agent":"SaradaHentaiCatalogue/4.0 (public read-only metadata)","Range":f"bytes={start}-{end}"})
            with urlopen(req,timeout=self.timeout) as r:
                return r.read(end-start+1)
        except HTTPError as e:
            self.errors.append({"url":u,"status":e.code,"error":"range_http_error"})
            e.close()
        except (URLError,TimeoutError,OSError) as e:
            self.errors.append({"url":u,"error":"range_"+type(e).__name__})
        return None
    def json(self,u):
        b=self.get(u)
        if b is None:return None
        try:return json.loads(b.decode("utf-8","replace"))
        except Exception:
            self.errors.append({"url":u,"error":"invalid_json"});return None

def mp4_duration(data):
    if not data:return None
    i=data.find(b"mvhd")
    if i<0 or i+24>len(data):return None
    version=data[i+4]
    try:
        if version==0:
            timescale=int.from_bytes(data[i+16:i+20],"big")
            duration=int.from_bytes(data[i+20:i+24],"big")
        elif version==1 and i+36<=len(data):
            timescale=int.from_bytes(data[i+24:i+28],"big")
            duration=int.from_bytes(data[i+28:i+36],"big")
        else:return None
        return round(duration/timescale,3) if timescale else None
    except Exception:return None

def classify(tag_names, category_names, rules):
    groups={k:[] for k in ("artists","characters","works")}
    mapping=rules.get("tag_types",{})
    classified_raw=set()
    for name in tag_names:
        kind=mapping.get(name)
        value=name
        if kind not in groups:
            match=re.fullmatch(r"(.+?)\s*\((artist|character|work)\)",name,re.I)
            if match:
                value=match.group(1).strip()
                kind={"artist":"artists","character":"characters","work":"works"}[match.group(2).lower()]
        if kind in groups:
            groups[kind].append(value)
            classified_raw.add(name)
    return {**{k:uniq(v) for k,v in groups.items()},
            "categories":uniq(category_names),"tags":uniq(tag_names),
            "unclassified_tags":[x for x in uniq(tag_names) if x not in classified_raw]}

def duration_seconds(s):
    m=re.fullmatch(r"PT(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?",s or "")
    if not m:return None
    h,mi,se=(float(x or 0) for x in m.groups())
    return round(h*3600+mi*60+se,3)

def main():
    ap=argparse.ArgumentParser(description="Catalogue public SaradaHentai V4")
    ap.add_argument("--base-url",default="https://saradahentai.com/")
    ap.add_argument("--output",default="saradahentai_v4_catalogue.json")
    ap.add_argument("--max-posts",type=int,default=100)
    ap.add_argument("--per-page",type=int,default=20)
    ap.add_argument("--delay",type=float,default=0.8)
    ap.add_argument("--timeout",type=int,default=20)
    ap.add_argument("--rules",help="JSON de classification explicite des tags")
    ap.add_argument("--no-gallery",action="store_true")
    ap.add_argument("--no-oembed",action="store_true")
    a=ap.parse_args()
    if a.max_posts<1 or not 1<=a.per_page<=100: ap.error("max-posts positif ; per-page entre 1 et 100")
    rules=json.loads(Path(a.rules).read_text(encoding="utf-8")) if a.rules else {}
    c=Client(a.base_url,a.delay,a.timeout)
    posts=[]; page=1
    while len(posts)<a.max_posts:
        n=min(a.per_page,a.max_posts-len(posts))
        u=c.base+"wp-json/wp/v2/posts?"+urlencode({"per_page":n,"page":page,"_embed":"1"})
        batch=c.json(u)
        if not isinstance(batch,list) or not batch: break
        posts.extend(batch); print("REST page",page,"=>",len(batch),file=sys.stderr)
        if len(batch)<n: break
        page+=1
    output=[]
    for i,p in enumerate(posts[:a.max_posts],1):
        print("Fiche",i,"/",len(posts),file=sys.stderr)
        link=p.get("link",""); pid=p.get("id")
        emb=(p.get("_embedded") or {}).get("wp:term") or []
        terms=[x for group in emb for x in group if isinstance(x,dict)]
        tag_names=[txt(x.get("name","")) for x in terms if x.get("taxonomy")=="post_tag"]
        cat_names=[txt(x.get("name","")) for x in terms if x.get("taxonomy")=="category"]
        def term_lookup(tax, ids, existing):
            names=list(existing)
            missing=[x for x in ids if not any(str(z.get("id"))==str(x) for z in terms)]
            for tid in missing:
                obj=c.json(c.base+"wp-json/wp/v2/"+tax+"/"+str(int(tid)))
                if isinstance(obj,dict) and obj.get("name"): names.append(txt(obj["name"]))
            return uniq(names)
        tag_names=term_lookup("tags",p.get("tags",[]),tag_names)
        cat_names=term_lookup("categories",p.get("categories",[]),cat_names)
        page_html=""; parser=Parser()
        raw=c.get(link,8000000) if link else None
        if raw:
            page_html=raw.decode("utf-8","replace")
            try:parser.feed(page_html)
            except Exception:pass
        featured=None
        fm=((p.get("_embedded") or {}).get("wp:featuredmedia") or [])
        if fm: featured=fm[0]
        if not featured and p.get("featured_media"):
            featured=c.json(c.base+"wp-json/wp/v2/media/"+str(p["featured_media"]))
        cover=None
        if isinstance(featured,dict):
            md=featured.get("media_details") or {}
            cover={"id":featured.get("id"),"url":featured.get("source_url"),
                   "alt":txt(featured.get("alt_text","")),"mime_type":featured.get("mime_type"),
                   "width":md.get("width"),"height":md.get("height"),
                   "sizes":{k:v.get("source_url") for k,v in (md.get("sizes") or {}).items() if v.get("source_url")}}
        gallery=[]
        if not a.no_gallery and pid:
            media=c.json(c.base+"wp-json/wp/v2/media?"+urlencode({"parent":pid,"per_page":100}))
            if isinstance(media,list):
                for m in media:
                    if m.get("id")==p.get("featured_media"):continue
                    if m.get("source_url"):
                        md=m.get("media_details") or {}
                        gallery.append({"id":m.get("id"),"url":m["source_url"],"mime_type":m.get("mime_type"),
                                        "alt":txt(m.get("alt_text","")),"width":md.get("width"),"height":md.get("height")})
        oembed=None
        if not a.no_oembed and link:
            o=c.json(c.base+"wp-json/oembed/1.0/embed?"+urlencode({"url":link,"format":"json"}))
            if isinstance(o,dict):oembed={"author_name":o.get("author_name"),"author_url":o.get("author_url")}
        videos=[]
        for rawurl,source in parser.videos:
            u=urljoin(link,rawurl)
            if c.allowed(u) and urlparse(u).path.lower().endswith(VIDEO_EXT):
                if u not in [x["url"] for x in videos]:videos.append({"url":u,"detected_by":source})
        for rawurl in re.findall(r"https?://[^ <>]+?\.(?:mp4|webm|m4v|mov|m3u8|mpd)",page_html,re.I):
            u=rawurl.rstrip(").,;")
            if c.allowed(u) and u not in [x["url"] for x in videos]:
                videos.append({"url":u,"detected_by":"page_source_url"})
        for k in ("og:video","og:video:url"):
            if parser.meta.get(k):
                u=urljoin(link,parser.meta[k])
                if c.allowed(u) and urlparse(u).path.lower().endswith(VIDEO_EXT) and u not in [x["url"] for x in videos]:
                    videos.append({"url":u,"detected_by":"meta:"+k})
        jsonld=[]
        for m in re.finditer(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>",page_html,re.I|re.S):
            try:
                data=json.loads(m.group(1)); stack=data if isinstance(data,list) else [data]
                while stack:
                    node=stack.pop()
                    if isinstance(node,dict):
                        if node.get("duration"):jsonld.append(node["duration"])
                        stack.extend(v for v in node.values() if isinstance(v,(dict,list)))
                    elif isinstance(node,list):stack.extend(node)
            except Exception:pass
        duration=next((duration_seconds(x) for x in jsonld if duration_seconds(x)!=None),None)
        duration_source="jsonld" if duration is not None else None
        if duration is None and videos and urlparse(videos[0]["url"]).path.lower().endswith(".mp4"):
            duration=mp4_duration(c.range(videos[0]["url"]))
            if duration is not None: duration_source="mp4_mvhd_range_1mib_max"
        credits=[]
        for x in parser.links:
            u=urljoin(link,x["href"]); host=(urlparse(u).hostname or "").lower()
            if host and host!=c.host and x["text"]:
                credits.append({"label":x["text"][:150],"url":u})
        credits=list({x["url"]:x for x in credits}.values())
        og=urljoin(link,parser.meta["og:image"]) if parser.meta.get("og:image") else None
        if not cover and og:cover={"url":og,"source":"og:image"}
        if cover and og:cover["og_image"]=og
        output.append({
          "metadata":{"id":pid,"title":txt((p.get("title") or {}).get("rendered","")),
                      "slug":p.get("slug"),"url":link,"date":p.get("date"),"modified":p.get("modified"),
                      "excerpt":txt((p.get("excerpt") or {}).get("rendered","")) or None,
                      "seo_description":parser.meta.get("description") or parser.meta.get("og:description"),
                      "content_text":txt((p.get("content") or {}).get("rendered","")) or None},
          "author":{"wordpress_id":p.get("author"),"public_name":(oembed or {}).get("author_name"),
                    "public_url":(oembed or {}).get("author_url"),"profile_details_status":"not_verified"},
          "classification":classify(tag_names,cat_names,rules),
          "taxonomy_ids":{"categories":p.get("categories",[]),"tags":p.get("tags",[])},
          "media":{"cover":cover,"gallery":gallery,
                   "video":{"url":videos[0]["url"] if videos else None,"detected_urls":videos,
                            "duration_seconds":duration,"duration_source":duration_source,
                            "quality":"single_published_variant_assumed"}},
          "credits":credits,
          "extraction":{"collected_at":datetime.now(timezone.utc).isoformat(),
                        "sources":["wordpress_rest","public_html","oembed"],
                        "warnings":[] if videos else ["no_video_url_observed"]}})
    result={"schema":"mihon-source-catalogue/0.4","extractor_version":"4.0.0","site":c.base,
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "summary":{"posts_collected":len(output),"errors":len(c.errors)},"posts":output,
            "errors":c.errors,
            "classification_note":"Les types artists/characters/works sont renseignés uniquement par les règles explicites. Les autres tags restent non classés."}
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Export :",a.output,"| publications :",len(output),"| erreurs :",len(c.errors),file=sys.stderr)

if __name__=="__main__":main()
