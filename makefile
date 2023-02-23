docker-build:
	@ docker image rm kafka_client:latest || (echo "Image kafka_client:latest didn't exist so not removed."; exit 0)
	docker build -t kafka_client:latest .

docker-run:
	docker-compose up -d

docker-down:
	docker compose down --remove-orphans 
# sink-post:
# 	@ curl --location --request POST 'http://localhost:8083/connectors' --header 'Content-Type: application/json' --data-raw '{"name": "jdbc-sink-1","config": {"connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector","connection.url": "jdbc:postgresql://postgres:5432/postgres","connection.user": "postgres","connection.password": "postgres","table.name.format": "process_data","topics": "my-topic-1","insert.mode": "insert","poll.interval.ms": 5000, "auto.create": "true","cleanup.policy": "compact","schemas.enable": "true", "pk.mode": "record_value","pk.fields": "timestamp", "delete.enabled":"false"}}'

# sink-del:
# 	curl --location --request DELETE 'http://localhost:8083/connectors/jdbc-sink-1'