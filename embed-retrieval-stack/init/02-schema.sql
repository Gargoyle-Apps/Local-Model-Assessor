-- Sample table for text + embeddings. Dimension MUST match your embedding model
-- (see versions.lock.yaml default_embedding_dimensions and model card).
-- To change N after init: migrate data or recreate volume — see README.

CREATE TABLE IF NOT EXISTS documents (
    id          bigserial PRIMARY KEY,
    content     text NOT NULL,
    metadata    jsonb DEFAULT '{}'::jsonb,
    embedding   vector(768) NOT NULL
);

-- Cosine distance is common for normalized embeddings; adjust opclass if you use L2 / inner product.
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw
    ON documents
    USING hnsw (embedding vector_cosine_ops);

COMMENT ON TABLE documents IS 'Sample RAG / semantic search table — copy or adapt in your app repo.';
