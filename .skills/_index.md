# Skills Index

Kit version: see `.skills/_meta.yml` (optional metadata only).

Load a skill only when the task clearly requires it.
Read the full `SKILL.md` only at that point — never preemptively.

| name | description | triggers |
|------|-------------|----------|
| skill-template | Canonical skill format and authoring reference | new skill, create skill, skill format |
| skill-author | How to write a skill from scratch | write skill, author skill |
| lma-python-env | Set up and use the repo-local Python virtualenv for all LMA scripts | python env, venv, pip install, bootstrap python, PEP 668, requirements.txt, scripts/py |
| lma-db-core | Init, migrate, and query the LMA SQLite database; data flow map and key queries | init database, migrate schema, query db, database setup, schema, db missing, migrate, schema error, data flow, key queries |
| lma-assess-import-model | Assess a new Ollama model, generate YAML, import to DB, and export the report | assess model, evaluate model, add model, import model, new model yaml, discover models, new models, ollama search, popular models, find models, who assessed, created_by, provenance, assessor |
| lma-hf-gguf-ollama | Import a HuggingFace GGUF model not in the Ollama library into the LMA workflow | GGUF, huggingface model, HF model, import GGUF, manual import, custom model |
| lma-mlx-lm | Run and assess MLX-format models on Apple Silicon via mlx-lm | MLX, mlx-lm, MLX LM, mlx model, mlx-community, Apple Silicon model, safetensors model |
| lma-model-selection | Select, recommend, or install an Ollama model for a given role or task | select model, which model, recommend model, model for coding, model for writing, best model, model details, model info, assessed models, model docs, install model, pull model, ollama pull, setup model |
| lma-ide-config | Generate IDE/agent config files from provisioned models in the DB | IDE config, configure IDE, continue config, cline config, generate config, agent config |
| lma-embed-stack-handoff | Generate embed-retrieval-stack handoff artifacts for app repos (Postgres + pgvector + AGE) | embed stack, pgvector, embeddings, postgres stack, vector database, AGE, graph database, stack handoff |

Add a row here whenever a new skill is added to `.skills/_skills/`.
