.phony:  graph-etl clean-db update-beerlist lint

graph-etl:
	pip3 install --quiet -r requirements.txt
	python3 config_neo4j_indexes.py
	python3 cloudburst_graph_etl.py

clean-db:
	neohelper detach-delete

update-beerlist:
	cd scrapers/scrape_cloudburst; \
	ls; \
	./0.curl_cb_website.sh; \
	./1.parse.py;
	cp scrapers/scrape_cloudburst/tmp/beers.json data/beers.json

lint:
	flake8
