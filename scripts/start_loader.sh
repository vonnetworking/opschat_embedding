#!/usr/bin/env bash
export ACTIVEMQ_HOST=10.128.135.97
export ACTIVEMQ_PORT=61616

export LOG_DIR=${LOG_DIR:-/tmp/docker_embedding_logs}
export EMBEDDING_CHUNK_SIZE=${EMBEDDING_CHUNK_SIZE:-256}
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2expo
export EMBEDDING_MODEL_LOCATION=sentence-transformers/all-MiniLM-L6-v2
export EMBEDDING_QUEUE=${EMBEDDING_QUEUE:-/queue/embedding}
# for testing
export EMBEDDING_QUEUE_LOCAL=true

# Start script
DIRNAME=$(dirname $0)
python ${DIRNAME}/../src/queue_loader.py
