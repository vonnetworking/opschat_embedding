EMBEDDING_WORKERS=${EMBEDDING_WORKERS:-2}

EMBEDDING_HOST_LOG_DIR=${EMBEDDING_HOST_LOG_DIR:-/tmp/docker_embedding_logs}
EMBEDDING_LOG_DIR=${EMBEDDING_LOG_DIR:-/tmp/docker_embedding_logs}

EMBEDDING_TEST=${EMBEDDING_TEST:-true}

mkdir -p ${EMBEDDING_HOST_LOG_DIR}

for I in $(seq 1 ${EMBEDDING_WORKERS}); do
	export J=`echo ${I}-1 | bc`
        export DOCKER_CONTAINER_NAME=embedding-app-${I}	
	
	docker rm --force ${DOCKER_CONTAINER_NAME:-embedding_app}
       	docker run \
	-d \
	-v ${EMBEDDING_HOST_LOG_DIR}:${EMBEDDING_LOG_DIR} \
	--gpus all \
	-e ACTIVEMQ_HOST=${ACTIVEMQ_HOST:-10.128.135.254} \
	-e ACTIVEMQ_PORT=61616 \
	-e EMBEDDING_LOG_DIR="${EMBEDDING_LOG_DIR}" \
	-e EMBEDDING_WORKER_NAME="${DOCKER_CONTAINER_NAME}" \
	-e EMBEDDING_MODEL=${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2expo} \
	-e EMBEDDING_MODEL_LOCATION=${EMBEDDING_MODEL_LOCATION:-sentence-transformers/all-MiniLM-L6-v2} \
	-e EMBEDDING_QUEUE=${EMBEDDING_QUEUE:-/queue/embedding} \
	-e EMBEDDING_TEST=${EMBEDDING_TEST:= } \
	-e EMBEDDING_CUDA_DEVICE="cuda:${J}" \
	-e VECTOR_STORE_QUEUE=${VECTOR_STORE_QUEUE:-/queue/vectorstore} \
	--name ${DOCKER_CONTAINER_NAME:-embedding_app} \
	${DOCKER_IMAGE:-tfearn/opschat-ingestion-app-w-gpu}
done
