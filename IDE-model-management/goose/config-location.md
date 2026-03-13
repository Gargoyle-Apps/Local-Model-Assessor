# Config location

**Docs:** [Goose — Configure LLM Provider](https://block.github.io/goose/docs/getting-started/providers)

**Config format:** YAML (`config.yaml`)

**Locations:**
- `~/.config/goose/config.yaml` — global config
- Custom providers: `~/.config/goose/custom_providers/*.json`

**How to configure:**
- CLI: `goose configure` → Configure Providers → Ollama
- Desktop: Settings → Models → Configure Providers → Ollama
- Or edit `config.yaml` directly (set `GOOSE_MODEL`)

**For Ollama:** Set `OLLAMA_HOST` (defaults to `http://localhost:11434`), then select model.

**To keep an untracked local copy in this repo folder:**
```bash
cp ~/.config/goose/config.yaml IDE-model-management/goose/config.yaml
```
