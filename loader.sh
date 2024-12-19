#!/usr/bin/env bash
export EMBEDDING_QUEUE=queue/embedding
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2expo
python queue_loader.py