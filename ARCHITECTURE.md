# Architecture

DocIntel treats document ingestion as a pipeline: normalize text, extract lightweight metadata, chunk deterministically, index terms, then expose search and routing. The lexical index is intentionally dependency-light and can be swapped for OpenSearch or a vector database while keeping the public service contract.
