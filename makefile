docker-build:
	@ docker image rm kafka_client:latest || (echo "Image kafka_client:latest didn't exist so not removed."; exit 0)
	docker build --no-cache -t kafka_client:latest .

docker-run:
	docker-compose up -d

docker-down:
	docker compose down

