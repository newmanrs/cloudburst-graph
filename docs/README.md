# Cloudburst Hop Graph

Web-scraping Cloudburst Brewing's beer descriptions to create a Neo4j graph database showing beers and hop varietals.

## Installation

Scrape webpage using provided
```
curl_cb_website.sh
```

A Neo4j installation is required.  The python scripts and provided docker scripts assume an environmental veriable for the database password is set as:
```
export NEO4j_PW="yourpassword"
```
and that the ports are still set to the defaults for the console of 7474, and bolt database driver on 7678.  A docker container script for setup is provided in `start_neo4j.sh`.

Parsing the website are done in a series of python scripts, starting with `parse.py`, `find_hops.py`, and `load_neo4j.py`.  These can be executed together with

```
./run_py.sh
```

## Example DB queries and images

Forthcoming



