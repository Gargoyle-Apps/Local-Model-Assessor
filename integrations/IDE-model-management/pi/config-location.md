# Config location

**Docs:** [Pi coding-agent docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/docs)

**Config format:** JSON

**Locations:**
- `~/.pi/agent/settings.json` — global settings (provider, model, thinking level)
- `.pi/settings.json` — project-level overrides
- `~/.pi/agent/models.json` — custom providers and models (Ollama, vLLM, etc.)
- `~/.pi/agent/auth.json` — credentials

**How to configure:**
- Interactive: `/settings` and `/model` commands inside Pi
- CLI: `pi --provider ollama --model model:tag`
- Or edit `settings.json` and `models.json` directly

**For Ollama:** Add provider in `models.json` with `baseUrl: "http://localhost:11434/v1"` and list models.

**To keep untracked local copies in this repo folder:**
```bash
cp ~/.pi/agent/settings.json integrations/IDE-model-management/pi/settings.json
cp ~/.pi/agent/models.json integrations/IDE-model-management/pi/models.json
```
