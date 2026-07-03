"""Pre-migration schema fixture for migrate-schema.sh tests."""

PRE_MIGRATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS models (
  model_id TEXT PRIMARY KEY,
  vram REAL NOT NULL,
  ctx INTEGER NOT NULL,
  class TEXT NOT NULL,
  tps INTEGER NOT NULL,
  url TEXT,
  install TEXT NOT NULL,
  vision INTEGER DEFAULT 0,
  tools INTEGER DEFAULT 0,
  reasoning INTEGER DEFAULT 0,
  moe INTEGER DEFAULT 0,
  fim INTEGER DEFAULT 0,
  structured INTEGER DEFAULT 0,
  creative TEXT,
  multilingual INTEGER DEFAULT 0,
  rag INTEGER DEFAULT 0,
  no_corun INTEGER DEFAULT 0,
  latency TEXT
);

CREATE TABLE IF NOT EXISTS role_model (
  role TEXT NOT NULL,
  variant TEXT NOT NULL,
  model_id TEXT NOT NULL,
  notes TEXT,
  PRIMARY KEY (role, variant),
  FOREIGN KEY (model_id) REFERENCES models(model_id)
);

CREATE TABLE IF NOT EXISTS constraint_model (
  constraint_name TEXT NOT NULL,
  model_id TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  PRIMARY KEY (constraint_name, model_id),
  FOREIGN KEY (model_id) REFERENCES models(model_id)
);

CREATE TABLE IF NOT EXISTS task_category (
  category TEXT NOT NULL,
  role_name TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  PRIMARY KEY (category, role_name)
);

CREATE TABLE IF NOT EXISTS decision_tree (
  need_key TEXT PRIMARY KEY,
  chain_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rag_pipeline (
  pipeline_name TEXT PRIMARY KEY,
  embedding_model TEXT,
  synthesis_model TEXT,
  generation_model TEXT,
  rules_model TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS model_docs (
  model_id TEXT PRIMARY KEY,
  spec_table TEXT,
  description TEXT,
  best_for TEXT,
  caveats TEXT,
  creative_tier TEXT
);

CREATE TABLE IF NOT EXISTS hardware_profile (
  id INTEGER PRIMARY KEY,
  yaml_content TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS software_profile (
  id INTEGER PRIMARY KEY,
  yaml_content TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);
"""
