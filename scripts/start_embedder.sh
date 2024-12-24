#!/usr/bin/env bash
export ACTIVEMQ_HOST=10.128.135.97
export ACTIVEMQ_PORT=61616

export LOG_DIR="/tmp/embedder_logs"
export WORKER_NAME="embedding-app-1"
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2expo
export EMBEDDING_MODEL_LOCATION=sentence-transformers/all-MiniLM-L6-v2
export EMBEDDING_QUEUE=/queue/embedding
# for testing
export EMBEDDING_QUEUE_LOCAL=True
export VECTOR_STORE_QUEUE=/queue/vectorstore
# Start script
DIRNAME=$(dirname $0)
python $DIRNAME/../src/app.py
