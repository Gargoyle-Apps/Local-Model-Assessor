# Config location

**Docs:** [OpenCode config reference](https://opencode.ai/docs/config/)

**Config format:** `opencode.json` or `opencode.jsonc` (JSON with Comments)

**Locations (precedence order):**
1. `~/.config/opencode/opencode.json` — global (user preferences)
2. `opencode.json` in project root — project-specific (overrides global)

**Project rules:** `.opencode/agents/*.md` — agent definitions loaded automatically

**To keep an untracked local copy in this repo folder:**
```bash
cp opencode.json IDE-model-management/opencode/opencode.json
# Or from global: cp ~/.config/opencode/opencode.json IDE-model-management/opencode/opencode.json
```
