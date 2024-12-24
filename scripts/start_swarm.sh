

# sudo vi /etc/docker/daemon.json
# sudo vi /etc/nvidia-container-runtime/config.toml
# https://gist.github.com/tomlankhorst/33da3c4b9edbde5c83fc1244f010815c

# docker swarm init --advertise-addr ${SWARM_MANAGER_IP:-10.128.135.97}
# docker network create --driver overlay swarm_network
docker service create --replicas ${SWARM_EMBEDDER_SERVICE_REPLICAS:-1} \
	--generic-resource "NVIDIA-GPU=0" \
	--network swarm_network \
        -e ACTIVEMQ_HOST=${ACTIVEMQ_HOST:-10.128.135.97} \
        -e ACTIVEMQ_PORT=61616 \
        -e EMBEDDING_MODEL=${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2expo} \
        -e EMBEDDING_MODEL_LOCATION=${EMBEDDING_MODEL_LOCATION:-sentence-transformers/all-MiniLM-L6-v2} \
        -e EMBEDDING_QUEUE=${EMBEDDING_QUEUE:-queue/embedding} \
        -e EMBEDDING_QUEUE_LOCAL=${EMBEDDING_QUEUE_LOCAL:= } \
        -e VECTOR_STORE_QUEUE=${VECTOR_STORE_QUEUE:-queue/vector-store} \
        --name ${DOCKER_CONTATINER_NAME:-embedding_app} \
        ${DOCKER_IMAGE:-tfearn/opschat-ingestion-app-w-gpu} 
