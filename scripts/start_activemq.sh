docker run \
	--detach \
	--name activemq \
	-p 61616:61616 \
	-p 8161:8161 \
	--rm \
	apache/activemq-artemis:latest-alpine
