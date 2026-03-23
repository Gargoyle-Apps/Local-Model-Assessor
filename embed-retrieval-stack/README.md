# Embed + retrieval stack (Postgres + pgvector + Apache AGE)

Docker-based **jumping-off point** for embeddings + vector search + optional property-graph queries in **one** PostgreSQL instance. This is **not** a full app framework — copy `embed-retrieval-stack/` (and generated handoff files) into your project when you are ready.

**Prerequisites:**

1. [Docker](https://docs.docker.com/get-docker/) and [Docker Compose v2](https://docs.docker.com/compose/).
2. **Local Model Assessor:** at least **one assessed embedding model** in `model-data/model-assessor.db` — a `models` row plus `role_model` with `role='embedding'` (and preferably a **provisioned** `provisioned_models` entry for `role='embedding'`). **`generate-stack-handoff.py` will exit with an error if none is configured.** The Docker stack itself does not require the SQLite DB; only the generated handoff + `embed_sample.py` do.

**Version pins:** [versions.lock.yaml](versions.lock.yaml) — do not float `:latest`; update the lock file when you intentionally upgrade.

### Version alignment (humans & LLMs)

Builds fail when **PostgreSQL major**, **Apache AGE**, and **pgvector** disagree (e.g. PG 18 API changes require a new enough pgvector). Use these **canonical upstream pages** to pick a matching set before editing `versions.lock.yaml`, `Dockerfile`, and `docker-compose.yml`:

| Component | Why you need it | Evergreen / release links |
|-----------|-----------------|---------------------------|
| **PostgreSQL** | Major version is fixed by the `apache/age:*` image and `postgresql-server-dev-XX` in the Dockerfile | [All release notes](https://www.postgresql.org/docs/release/) · [Version support policy](https://www.postgresql.org/support/versioning/) |
| **Apache AGE** | Docker tag encodes PG major (`release_PG18_1.7.0`, etc.) | [GitHub releases](https://github.com/apache/age/releases) · [Docker Hub tags](https://hub.docker.com/r/apache/age/tags) · [AGE docs](https://age.apache.org/) |
| **pgvector** | Compiled against the **same** server headers as the running Postgres (extension API must match) | [GitHub releases](https://github.com/pgvector/pgvector/releases) · [Installation / compatibility](https://github.com/pgvector/pgvector#installation) · [Issues (search “PostgreSQL 18” or your major)](https://github.com/pgvector/pgvector/issues) |

**Heuristic for another LLM:** (1) Read `postgres_major` and `apache_age_tag` in `versions.lock.yaml`. (2) Confirm the AGE tag exists on Docker Hub. (3) Choose a **pgvector git tag** from [releases](https://github.com/pgvector/pgvector/releases) whose release notes or build match that Postgres major; if the build fails on extension C API errors, open the pgvector issues link above and bump the tag. (4) Keep `postgresql-server-dev-XX` in the Dockerfile aligned with `postgres_major`.

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
| [pgvector](https://github.com/pgvector/pgvector) **v0.8.2** (built in Dockerfile; PG18-compatible) | **vector** type + HNSW / IVFFlat indexes |
| `init/*.sql` | `CREATE EXTENSION vector` + sample `documents` table |

**Apple Silicon:** The pinned `apache/age` tag lists **linux/arm64** on Docker Hub (verify before upgrading tags). If a future pin is amd64-only, the README in `versions.lock.yaml` should call it out.

---

## Troubleshooting

**`failed to connect to the docker API` / `docker.sock` missing** — Start **Docker Desktop** (or your Docker engine) and wait until it is running; then retry `docker compose up`.

**Image build fails on `vacuum_delay_point` / pgvector compile** — PostgreSQL 18 changed that API; use a **pgvector** release that supports your Postgres major (see [pgvector releases](https://github.com/pgvector/pgvector/releases); this repo pins **v0.8.2+** for PG18 in [versions.lock.yaml](versions.lock.yaml)). For the full upgrade workflow, use **§ Version alignment** above. After changing the pin, rebuild: `docker compose build --no-cache`.

### “Started” but not healthy / can’t connect

**Run every command from the directory that contains `docker-compose.yml`** (this folder: `embed-retrieval-stack/`). If you see `no configuration file provided`, you are in the wrong directory.

Copy **one line at a time** (don’t paste comment lines — they confuse some shells).

```bash
cd /path/to/Local-Model-Assessor/embed-retrieval-stack
```

```bash
docker compose ps -a
```

```bash
docker compose up -d --build
```

```bash
docker compose logs postgres
```

If the service exits, the **last lines** of `docker compose logs postgres` usually show the SQL or config error.

Container name is fixed in compose as `lma-postgres-stack`. If `docker inspect` says **no such object**, the container was never created or was removed — use `docker compose ps -a` first.

```bash
docker inspect lma-postgres-stack --format 'Status={{.State.Status}} Exit={{.State.ExitCode}} Health={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}'
```

When the service is **running**:

```bash
docker compose exec postgres pg_isready -U lma -d lma
```

**First boot** can take **up to ~1–2 minutes** while init scripts run (`docker-entrypoint-initdb.d`). The compose **healthcheck** allows **90s** `start_period` before failed checks count as unhealthy.

**`Restarting (1)` and logs say “18+, these Docker images…” / `/var/lib/postgresql/data (unused mount)`** — Postgres **18+** changed where data lives; the volume must mount at **`/var/lib/postgresql`**, not `/var/lib/postgresql/data` ([docker-library/postgres#1259](https://github.com/docker-library/postgres/pull/1259)). This repo’s `docker-compose.yml` uses the correct path. If you still crash after updating compose, the **old volume** was created with the wrong layout — remove it once (destroys local DB data in that volume):

```bash
docker compose down
docker volume rm embed-retrieval-stack_lma_pgdata
docker compose up -d --build
```

(`docker volume ls | grep lma` if the name differs.)

**Stale or broken data volume** (other init/SQL errors):

```bash
docker compose down
docker volume rm embed-retrieval-stack_lma_pgdata
docker compose up -d --build
```

**Port already in use** on the host (`5432`):

```bash
lsof -i :5432
```

Set `POSTGRES_PORT=5433` in `.env` and reconnect using that port.

**Run in the foreground** to see errors immediately:

```bash
docker compose up --build
```

---

## Ollama

This stack **does not** run Ollama. Install and run Ollama on the host (or another container) and use the embedding model you selected in Local Model Assessor. `embed_sample.py` defaults to `OLLAMA_HOST=http://127.0.0.1:11434`.

---

## Links

- [pgvector](https://github.com/pgvector/pgvector)
- [Apache AGE](https://age.apache.org/)
- [Ollama](https://ollama.com)
