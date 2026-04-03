---
name: lma-ide-config
description: "Generate IDE/agent config files from provisioned models in the DB."
triggers:
  - IDE config
  - configure IDE
  - continue config
  - cline config
  - generate config
  - agent config
dependencies:
  - lma-python-env
  - lma-db-core
version: "1.0.0"
---

# LMA IDE Config

## When to use this skill

Load when the user wants to generate or update IDE/agent configuration files (Continue, Cline, or other supported targets) from the provisioned models in the database.

## Instructions

### 1. Generate config

```bash
./scripts/py scripts/generate-ide-config.py --target continue|cline [--active-only] [--dry-run]
```

| Flag | Purpose |
|------|---------|
| `--target` | Required. Which IDE/agent to generate for (`continue`, `cline`). |
| `--active-only` | Only include provisioned models where `is_active = 1`. |
| `--dry-run` | Print what would be written without writing files. |

Output goes to `integrations/IDE-model-management/<app>/` with role-appropriate timeouts.

### 2. Supported targets

See `integrations/IDE-model-management/IDE.md` for:
- Per-app config locations and formats.
- Timeout recommendations by role.
- Manual setup instructions for apps not yet supported by the generator.

Config location docs for individual apps are at `integrations/IDE-model-management/<app>/config-location.md`.

### 3. Auto-generation after profile import

After running `import-profiles.py`, if `software-profile.yaml` names a supported app, the IDE config can be regenerated automatically.

### 4. Other apps (manual)

For apps without generator support (Zed, Goose, Pi, OpenCode), follow the manual instructions in `integrations/IDE-model-management/IDE.md`.

## Notes

- Generated config files under `integrations/IDE-model-management/*/config.*` are gitignored.
- `integrations/IDE-model-management/cline/provider-settings.json` is also gitignored.
- The generator reads `provisioned_models` and `models` from the DB.
