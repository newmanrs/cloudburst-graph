docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v /root/neo4j/data:/data \
    -v /root/neo4j/logs:/logs \
    -v /root/neo4j/import:/var/lib/neo4j/import \
    -v /root/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/${NEO4J_PW} \
    --env NEO4J_dbms_connector_bolt_listen__address=0.0.0.0:7687 \
	neo4j
