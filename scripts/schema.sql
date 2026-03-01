-- Local Model Assessor Database Schema
-- SQLite 3.x — single source of truth for models, profiles, and assessments

-- Meta / config (replaces _meta, recommended_fleet)
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

-- Models: core model specifications
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
  latency TEXT,
  assessed_at TEXT DEFAULT (datetime('now'))
);

-- Role assignments: by_role.{role}.{variant} → model
CREATE TABLE IF NOT EXISTS role_model (
  role TEXT NOT NULL,
  variant TEXT NOT NULL,
  model_id TEXT NOT NULL,
  notes TEXT,
  PRIMARY KEY (role, variant),
  FOREIGN KEY (model_id) REFERENCES models(model_id)
);

-- Constraint assignments: by_constraint.{constraint} → models
CREATE TABLE IF NOT EXISTS constraint_model (
  constraint_name TEXT NOT NULL,
  model_id TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  PRIMARY KEY (constraint_name, model_id),
  FOREIGN KEY (model_id) REFERENCES models(model_id)
);

-- Task categories: by_task_category.{category} → roles
CREATE TABLE IF NOT EXISTS task_category (
  category TEXT NOT NULL,
  role_name TEXT NOT NULL,
  sort_order INTEGER DEFAULT 0,
  PRIMARY KEY (category, role_name)
);

-- Decision tree: need_* → fallback chain
CREATE TABLE IF NOT EXISTS decision_tree (
  need_key TEXT PRIMARY KEY,
  chain_text TEXT NOT NULL
);

-- RAG pipelines
CREATE TABLE IF NOT EXISTS rag_pipeline (
  pipeline_name TEXT PRIMARY KEY,
  embedding_model TEXT,
  synthesis_model TEXT,
  generation_model TEXT,
  rules_model TEXT,
  notes TEXT
);

-- Model documentation (for assessed-models.md generation)
CREATE TABLE IF NOT EXISTS model_docs (
  model_id TEXT PRIMARY KEY,
  spec_table TEXT,
  description TEXT,
  best_for TEXT,
  caveats TEXT,
  creative_tier TEXT,
  FOREIGN KEY (model_id) REFERENCES models(model_id)
);

-- Hardware profile (consolidated)
CREATE TABLE IF NOT EXISTS hardware_profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  yaml_content TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Software profile (consolidated)
CREATE TABLE IF NOT EXISTS software_profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  yaml_content TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_models_class ON models(class);
CREATE INDEX IF NOT EXISTS idx_models_vram ON models(vram);
CREATE INDEX IF NOT EXISTS idx_role_model_role ON role_model(role);
CREATE INDEX IF NOT EXISTS idx_constraint_model_constraint ON constraint_model(constraint_name);
