# Cloudburst Hop Graph

Web-scraping [Cloudburst Brewing's](https://cloudburstbrew.com/) beer descriptions to create a Neo4j graph database showing relationships between various beers and hop varietals.

![azacca](img/azacca.svg)

## Installation

Scrape webpage using provided
```
curl_cb_website.sh
```

A [Neo4j](https://neo4j.com/) installation is required.  The python scripts and provided docker scripts assume an environmental variable for the database password is set as:
```
export NEO4j_PW="yourpassword"
```
with the default user `neo4j`, and that the ports are still set to the defaults for the console of 7474, and bolt database driver on 7678.  A sample docker script for setup of Neo4j is provided in `start_neo4j.sh`, but you may install Neo4j however you wish.

Parsing the website are done in a series of python scripts, starting with `parse.py` (parses the html file generated with curl script), `find_hops.py` (check descriptions from site for hop mentions), and `load_neo4j.py` (load DB).  These can be executed together with

```
./run_py.sh
```

Be mindful that making changes to these scripts and reexecuting may require you to manually wipe the neo4j database from the console with `match (n) detach delete (n)`.  

## Example DB queries

### Beers containing a hop (and their styles)

I claim these are among the most delicious.

```
match p = (h:Hop)-[]-(b:Beer)-[]-(s:Style)
where h.name = 'Azacca'
return p
```

![azacca](img/azacca.svg)

### All beers of a particular style and their hop graph

```
match p = (h:Hop)-[]-(b:Beer)-[]-(s:Style)
where s.style = 'Pale'
return p
```
![pales](img/pale_ales_hops.svg)


###  Largest ABV
```
match (b:Beer)
with b order by b.abv DESC
return b.name, b.abv, b.style limit 10
```

### Most frequent hop pairings

```
match p = (a:Hop)-[]-(b:Beer)-[]-(c:Hop)
where a.name < c.name
return a.name as hop1, c.name as hop2, count(b) as count, collect(b.name) as beer_list order by count DESC
```
