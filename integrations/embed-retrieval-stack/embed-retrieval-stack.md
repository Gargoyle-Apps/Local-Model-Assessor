# Embed + retrieval stack (Postgres + pgvector + Apache AGE)

Docker **jumping-off point** for embeddings + vectors + optional **Apache AGE** graphs in one Postgres — not an app framework. Copy **`integrations/embed-retrieval-stack/`** (this folder) + handoff outputs into your app repo when ready.

**`psql`:** use **`docker compose exec postgres psql …`** only; the image includes the client. Apps use **`DATABASE_URL`** + a driver (e.g. `psycopg`). Host **`libpq`** / [Brewfile](../../Brewfile) is unrelated to this workflow (keg-only; conflicts full PostgreSQL — `brew info libpq`).

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) + [Compose v2](https://docs.docker.com/compose/). **Handoff script** (`generate-stack-handoff.py`) needs an assessed **embedding** in `model-assessor.db` (`models` + `role_model.embedding` / provisioned); the compose stack alone does not need SQLite.

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

## Common use cases

- **Semantic search** — meaning, not keywords.
- **RAG** — chunk → embed → retrieve → chat; FAQs/support docs.
- **Multimodal search** — needs **image+text** embedder in LMA; text-only embedders won’t search images.
- **Recommendations** — nearest neighbors over item vectors.
- **Dedup / clustering** — vectors for cleanup and coarse grouping.

**AGE:** optional Cypher graphs beside pgvector — [Apache AGE](https://github.com/apache/age).

---

## Quick start

From the **repository root**:

```bash
cd integrations/embed-retrieval-stack
cp .env.example .env
# Edit .env — set a strong POSTGRES_PASSWORD for anything beyond local dev

docker compose up -d --build
```

**First boot:** `up -d` returns before Postgres listens (often **15–60s** init). Early `pg_isready` / `exec psql` → `no response` or exit 2 is normal — wait, or use `until … pg_isready` (below). Don’t chain `up && … pg_isready` without a wait.

**New volume only** for init scripts. Reused volume missing **`vector`** / **`documents`** → `down` + `docker volume rm embed-retrieval-stack_lma_pgdata` + `up` (see Troubleshooting).

Watch until you see *database system is ready to accept connections*:

```bash
docker compose logs -f postgres
```

Or poll (stop with Ctrl+C when it prints `accepting connections` / exit 0):

```bash
until docker compose exec postgres pg_isready -U lma -d lma; do sleep 2; done
```

Then verify extensions (works without host `psql`):

```bash
docker compose exec postgres psql -U lma -d lma -c "SELECT extname FROM pg_extension ORDER BY 1;"
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
- **Duplicate:** copy this directory (in Local Model Assessor: `integrations/embed-retrieval-stack/`, including Dockerfile, `docker-compose.yml`, `init/`, `versions.lock.yaml`, `.env.example`, this doc) into your application repo and run compose there. You may rename the folder to `embed-retrieval-stack` in the destination if you prefer.

Also generate a tailored handoff from your assessed models (**requires embedding prerequisite above**):

```bash
# From repository root
python3 scripts/generate-stack-handoff.py
```

Outputs (gitignored by default) include `STACK_HANDOFF.md` and `embed_sample.py` with your **embedding** alias from `model-assessor.db`. See [AGENTS.md](../../AGENTS.md) task routing.

---

## Architecture

| Piece | Role |
|-------|------|
| [apache/age](https://hub.docker.com/r/apache/age) `release_PG18_1.7.0` | PostgreSQL 18 + **Apache AGE** |
| [pgvector](https://github.com/pgvector/pgvector) **v0.8.2** (built in Dockerfile; PG18-compatible) | **vector** type + HNSW / IVFFlat indexes |
| `init/*.sql` | `CREATE EXTENSION vector` + sample `documents` table |

**Apple Silicon:** The pinned `apache/age` tag lists **linux/arm64** on Docker Hub (verify before upgrading tags). If a future pin is amd64-only, the note in [versions.lock.yaml](versions.lock.yaml) should call it out.

---

## Troubleshooting

**`failed to connect to the docker API` / `docker.sock` missing** — Start **Docker Desktop** (or your Docker engine) and wait until it is running; then retry `docker compose up`.

**Image build fails on `vacuum_delay_point` / pgvector compile** — PostgreSQL 18 changed that API; use a **pgvector** release that supports your Postgres major (see [pgvector releases](https://github.com/pgvector/pgvector/releases); this repo pins **v0.8.2+** for PG18 in [versions.lock.yaml](versions.lock.yaml)). For the full upgrade workflow, use **Version alignment** above. After changing the pin, rebuild: `docker compose build --no-cache`.

### “Started” but not healthy / can’t connect

**Run every command from the directory that contains `docker-compose.yml`** (in this repo: `integrations/embed-retrieval-stack/`). If you see `no configuration file provided`, you are in the wrong directory.

Copy **one line at a time** (don’t paste comment lines — they confuse some shells).

```bash
cd /path/to/Local-Model-Assessor/integrations/embed-retrieval-stack
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

**`Restarting (1)` + “18+ … unused mount”** — PG18+ needs volume on **`/var/lib/postgresql`** (this compose is correct); **old wrong-layout volume** must go once. **Also** after bad init / missing `vector`: same reset:

```bash
docker compose down
docker volume rm embed-retrieval-stack_lma_pgdata   # adjust: docker volume ls | grep lma
docker compose up -d --build
```

**Port in use** (`5432`):

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

Not in this compose — run on host (or elsewhere). `embed_sample.py` defaults to `OLLAMA_HOST=http://127.0.0.1:11434`.
