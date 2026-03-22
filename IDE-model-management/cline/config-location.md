# Config location

**Applies to:** Cline and Roo Code (VS Code extensions)

**Cline docs:** [Cline — GitHub](https://github.com/cline/cline)
**Roo Code docs:** [Roo Code — GitHub](https://github.com/RooVetGit/Roo-Code)

**Config format:** JSON — provider settings are typically edited through the extension's settings panel or exported/imported as JSON.

**Key timeout field:** `requestTimeoutMs` inside the API provider configuration. For Ollama, the provider block includes `apiProvider`, `ollamaModelId`, `apiBaseUrl`, and `requestTimeoutMs`.

**Roo Code embedding:** Roo's local embedding model may have a separate, historically aggressive timeout. If using a Snappy-class embedding alias, verify that the embedding timeout is also raised.

**Locations:**
- **Cline:** VS Code settings → Cline extension → API Configuration (exported via extension UI)
- **Roo Code:** VS Code settings → Roo Code extension → API Configuration

**Export shape may differ:** The generated `provider-settings.json` is a map of alias-based keys to `{ apiConfiguration: … }` blocks. Real Cline/Roo exports may use a different top-level schema depending on extension version. Compare the generated file to an export from your extension and merge fields if the root structure differs.

**Profile keys:** Each entry is keyed by a sanitized alias (colons replaced with dashes, e.g. `qwen3-30b_coding_8k`), so multiple base models sharing the same role never collide.

**To keep an untracked local copy in this repo folder:**
```bash
# After exporting from the extension, save here:
cp ~/path/to/exported-settings.json IDE-model-management/cline/provider-settings.json
```
