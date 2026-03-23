# Local Model Assessor — Homebrew Bundle (NOT required for embed-retrieval-stack)
# https://docs.brew.sh/Manpage#bundle-subcommand
#
# From the repository root:
#   brew bundle
#
# Python deps for scripts stay in requirements.txt (pip), not here.
#
# For Docker Postgres in this repo, use:
#   docker compose exec postgres psql …
#
# Homebrew caveat for libpq (always read `brew info libpq` after install):
#   libpq is keg-only, which means it was not symlinked into /opt/homebrew,
#   because it conflicts with PostgreSQL.
# You must add opt/libpq/bin to PATH yourself if you want host psql/pg_dump.

brew "libpq"

# Docker Desktop — uncomment only if you want brew to install it (omit if already installed).
# cask "docker"
