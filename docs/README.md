# Cloudburst Hop Graph

Web-scraping [Cloudburst Brewing's](https://cloudburstbrew.com/) beer descriptions to create a Neo4j graph database showing relationships between various beers and hop varietals.

## Installation

Scrape webpage using provided
```
curl_cb_website.sh
```

A [Neo4j](https://neo4j.com/) installation is required.  The python scripts and provided docker scripts assume an environmental variable for the database password is set as:
```
export NEO4j_PW="yourpassword"
```
with the default user `neo4j`, and that the ports are still set to the defaults for the console of 7474, and bolt database driver on 7678.  A docker container script for setup of Neo4j is provided in `start_neo4j.sh`.

Parsing the website are done in a series of python scripts, starting with `parse.py` (parses the html file generated with curl script), `find_hops.py` (check descriptions from site for hop mentions), and `load_neo4j.py` (load DB).  These can be executed together with

```
./run_py.sh
```

Be mindful if making changes to these scripts and re-executing may require you to manually wipe the neo4j database from the console with `match (n) detach delete (n)`

## Example DB queries and images

Forthcoming
