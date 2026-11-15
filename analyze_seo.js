const fs = require('fs');
const path = require('path');

const skillsDir = '.opencode/skills';
const seoSkills = fs.readdirSync(skillsDir).filter(f => f.startsWith('seo'));

const results = [];

for (const skill of seoSkills) {
    const skillPath = path.join(skillsDir, skill);
    const skillMd = fs.readFileSync(path.join(skillPath, 'SKILL.md'), 'utf-8');
    
    // Check for dependencies
    const hasPython = /python|pip|venv/i.test(skillMd);
    const hasScripts = fs.existsSync(path.join(skillPath, 'scripts'));
    const hasAgents = fs.existsSync(path.join(skillPath, 'agents')) || /subagent|agents\//i.test(skillMd);
    const hasExternalAPI = /DATAFORSEO|PageSpeed|GSC|GA4|Moz|SE Ranking|API_KEY|env/i.test(skillMd);
    const hasExternalPaths = /~\/|CLAUDE_PLUGIN_ROOT/i.test(skillMd);
    
    let classification = 'A';
    let dependencies = [];

    if (hasPython) dependencies.push('python/pip');
    if (hasScripts) dependencies.push('scripts/');
    if (hasAgents) dependencies.push('agents/subagents');
    if (hasExternalAPI) dependencies.push('API Keys (DataForSEO/GSC/etc)');
    if (hasExternalPaths) dependencies.push('External Paths');

    if (dependencies.length > 0) {
        classification = dependencies.some(d => d.includes('API') || d.includes('Paths') || d.includes('python')) ? 'C' : 'B';
    }

    results.push({ skill, classification, dependencies: dependencies.join(', ') || 'None' });
}

console.log(JSON.stringify(results, null, 2));
