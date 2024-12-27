# SCENARIOS="1/1024,1,1024 2/1024,2,1024 3/1024,3,1024 4/1024,4,1024 1/512,1,512 2/512,2,512 3/512,3,512 4/512,4,512 1/128,1,128 2/128,2,128 3/128,3,128 4/128,4,128 1/64,1,64 2/64,2,64 3/64,3,64 4/64,4,64"

SCENARIOS="1/1024,1,1024 2/1024,2,1024 3/1024,3,1024 4/1024,4,1024 1/2048,1,2048 2/2048,2,2048 3/2048,3,2048 4/2048,4,2048 1/3072,1,3072 2/3072,2,3072 3/3072,3,3072 4/3072,4,3072"  

export EMBEDDING_LOG_DIR="/tmp/docker_embedding_logs"
export EMBEDDING_TEST="true"

for SCENARIO in ${SCENARIOS}; do
	export NAME=`echo $SCENARIO | awk -F',' '{print $1}'`
	export EMBEDDING_WORKERS=`echo $SCENARIO | awk -F',' '{print $2}'` 
	export EMBEDDING_CHUNK_SIZE=`echo $SCENARIO | awk -F',' '{print $3}'`
	echo "Running: ${NAME}, WORKERS: ${EMBEDDING_WORKERS}, CHUNK_SIZE: ${EMBEDDING_CHUNK_SIZE}"

	DIRNAME=$(dirname $0)
	${DIRNAME}/stop_docker_embedding.sh
	sleep 2
	rm -f ${EMBEDDING_LOG_DIR}/*.log

	${DIRNAME}/start_docker_embedding.sh
	
	sleep 10
	${DIRNAME}/start_loader.sh
	${DIRNAME}/stop_docker_embedding.sh
done
