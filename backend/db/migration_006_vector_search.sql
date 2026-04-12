-- Migration 006: Vector search for RAG research articles
-- Run in Supabase SQL Editor
--
-- Enables pgvector extension and creates a table for storing
-- research article section embeddings with semantic search.

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Research sections with embeddings
CREATE TABLE IF NOT EXISTS research_sections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain TEXT NOT NULL,
  section_title TEXT NOT NULL,
  content TEXT NOT NULL,
  token_count INT,
  embedding VECTOR(768),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_sections_domain ON research_sections(domain);

-- HNSW index for fast approximate nearest neighbor search
-- cosine distance operator: <=>
CREATE INDEX IF NOT EXISTS idx_research_sections_embedding
  ON research_sections USING hnsw (embedding vector_cosine_ops);

-- RPC function for similarity search (required because PostgREST
-- does not expose pgvector operators directly)
CREATE OR REPLACE FUNCTION match_research_sections(
  query_embedding VECTOR(768),
  match_count INT DEFAULT 10,
  similarity_threshold FLOAT DEFAULT 0.5
)
RETURNS TABLE (
  id UUID,
  domain TEXT,
  section_title TEXT,
  content TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    rs.id,
    rs.domain,
    rs.section_title,
    rs.content,
    (1 - (rs.embedding <=> query_embedding))::FLOAT AS similarity
  FROM research_sections rs
  WHERE (1 - (rs.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY rs.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
