DOCKER_CONTAINER_NAME=embedding-app-

for CONTAINER in `docker ps | awk '{print $NF}' | grep ${DOCKER_CONTAINER_NAME}`; do
	docker rm -f ${CONTAINER}
done
