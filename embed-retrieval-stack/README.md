# Embed + retrieval stack (Postgres + pgvector + Apache AGE)

Docker-based **jumping-off point** for embeddings + vector search + optional property-graph queries in **one** PostgreSQL instance. This is **not** a full app framework — copy `embed-retrieval-stack/` (and generated handoff files) into your project when you are ready.

**Prerequisites:**

1. [Docker](https://docs.docker.com/get-docker/) and [Docker Compose v2](https://docs.docker.com/compose/).
2. **Local Model Assessor:** at least **one assessed embedding model** in `model-data/model-assessor.db` — a `models` row plus `role_model` with `role='embedding'` (and preferably a **provisioned** `provisioned_models` entry for `role='embedding'`). **`generate-stack-handoff.py` will exit with an error if none is configured.** The Docker stack itself does not require the SQLite DB; only the generated handoff + `embed_sample.py` do.

**Version pins:** [versions.lock.yaml](versions.lock.yaml) — do not float `:latest`; update the lock file when you intentionally upgrade.

---

## Common use cases (why embeddings + pgvector)

1. **“Smart” search (semantic search)** — Keyword search misses paraphrases (“car” vs “automobile”). Embeddings let you query notes or files by *meaning*—e.g. search “feeling burnt out” and surface entries about exhaustion or work stress without exact phrase matches.

2. **Chat with your own data (RAG)** — Chunk PDFs, tickets, or diaries, embed each chunk, store vectors, retrieve top matches for a user question, then pass those chunks to a chat model. Enables questions like “What did my accountant say about 2023 taxes?” grounded in *your* documents. The same pattern supports **FAQ / support bots** instead of rigid “press 1” trees when your answers live in docs.

3. **Find media by description (multimodal)** — With **image+text** embedding models, you can search photos by natural language (“dog in snow”, “coffee receipt”) instead of filenames like `IMG_9482.jpg`. **Plain text embedders alone do not do this** — assess and provision a **multimodal** model in Local Model Assessor if you need image search.

4. **“You might also like” (recommendations)** — Represent posts, products, or articles as vectors; nearest neighbors in the database surface conceptually similar items for blogs, shops, or internal wikis without hand-built tag trees.

5. **Dedup, clustering, and light taxonomy** — Near-duplicate docs/emails/attachments often sit close together in vector space—useful for cleanup. Unlabeled piles (bookmarks, recipes, research links) can be **clustered** into coarse topics (“Mexican recipes”, “DIY”) before you manually organize.

**Apache AGE (graphs):** Extensions load side-by-side with pgvector. Graph modeling (Cypher, property graphs) is **optional** for v1; see [Apache AGE](https://github.com/apache/age) when you need graph traversal on top of relational + vector data.

---

## Quick start

From the **repository root**:

```bash
cd embed-retrieval-stack
cp .env.example .env
# Edit .env — set a strong POSTGRES_PASSWORD for anything beyond local dev

docker compose up -d --build
```

Wait for healthcheck, then connect:

```bash
psql "postgresql://lma:lma_dev_change_me@localhost:5432/lma" -c "SELECT extname FROM pg_extension ORDER BY 1;"
```

You should see `age` and `vector` among installed extensions.

---

## Embedding dimension (critical)

The sample table uses `vector(768)` in [init/02-schema.sql](init/02-schema.sql). **Your model’s output dimension must match** or inserts will fail. Check the Ollama/model card for the embedding model you assessed (e.g. 768, 1024, …). To use a different `N`:

- **Before first run:** edit `init/02-schema.sql` and rebuild with a fresh volume, **or**
- **After data exists:** create a new column/table with the correct `N` and migrate — do not change `N` in place casually.

`default_embedding_dimensions` in [versions.lock.yaml](versions.lock.yaml) documents the sample schema default.

---

## Copy into another repo

You can either:

- **Reuse one stack:** keep this compose project running; point your app at `DATABASE_URL` on `localhost` (or Docker network hostname if the app is containerized).
- **Duplicate:** copy `embed-retrieval-stack/` (Dockerfile, `docker-compose.yml`, `init/`, `versions.lock.yaml`, `.env.example`) into your application repo and run compose there.

Also generate a tailored handoff from your assessed models (**requires embedding prerequisite above**):

```bash
# From repository root
python3 scripts/generate-stack-handoff.py
```

Outputs (gitignored by default) include `STACK_HANDOFF.md` and `embed_sample.py` with your **embedding** alias from `model-assessor.db`. See [AGENTS.md](../AGENTS.md) task routing.

---

## Architecture

| Piece | Role |
|-------|------|
| [apache/age](https://hub.docker.com/r/apache/age) `release_PG18_1.7.0` | PostgreSQL 18 + **Apache AGE** |
| [pgvector](https://github.com/pgvector/pgvector) (built in Dockerfile) | **vector** type + HNSW / IVFFlat indexes |
| `init/*.sql` | `CREATE EXTENSION vector` + sample `documents` table |

**Apple Silicon:** The pinned `apache/age` tag lists **linux/arm64** on Docker Hub (verify before upgrading tags). If a future pin is amd64-only, the README in `versions.lock.yaml` should call it out.

---

## Ollama

This stack **does not** run Ollama. Install and run Ollama on the host (or another container) and use the embedding model you selected in Local Model Assessor. `embed_sample.py` defaults to `OLLAMA_HOST=http://127.0.0.1:11434`.

---

## Links

- [pgvector](https://github.com/pgvector/pgvector)
- [Apache AGE](https://age.apache.org/)
- [Ollama](https://ollama.com)
