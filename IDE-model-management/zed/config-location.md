# Config location

**Docs:** [Zed AI — LLM Providers](https://zed.dev/docs/ai/llm-providers), [Configuration](https://zed.dev/docs/ai/configuration)

**Config format:** JSON (`settings.json`)

**Locations:**
- `~/.config/zed/settings.json` — global (user preferences)
- `.zed/settings.json` — project-level overrides

**Ollama config:** Under `language_models.ollama` in `settings.json`. Zed auto-discovers pulled Ollama models, or you can list them explicitly with `available_models`.

**Per-model options:** `name`, `display_name`, `max_tokens` (context), `keep_alive`, `supports_tools`, `supports_thinking`, `supports_images`.

**To keep an untracked local copy in this repo folder:**
```bash
cp ~/.config/zed/settings.json IDE-model-management/zed/settings.json
```
