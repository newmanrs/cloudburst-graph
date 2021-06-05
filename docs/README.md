# Cloudburst Hop Graph

Web-scraping [Cloudburst Brewing's](https://cloudburstbrew.com/) beer descriptions to create a Neo4j graph database showing relationships between various beers and hop varietals.  

![azacca](img/azacca.svg)

Additional examples are shown below in the [example queries](#example-db-queries) and [Neo4j Bloom](#neo4j-bloom) sections.

## Installation

Project needs some flavor of Linux shell to function (Windows Subsystem for Linux, Linux, OSX etc) and a copy of Neo4j installed locally.
A sample docker script for setup of Neo4j is provided in `start_neo4j.sh`, but you may want to consider using Neo4j Desktop as it also installs Neo4j Bloom on your local which provides a GPU-accelerated GUI that can be set up for more natural searching than the standard Neo4j database console.  

The python scripts and provided docker scripts assume an environmental variable for the database password is set as:
```
export NEO4j_PW="yourpassword"
```
with the default user `neo4j`, and that the ports are still set to the defaults for the console of 7474, and bolt database driver on 7678.  

Scrape webpage using provided
```
curl_cb_website.sh
```

Parsing the website are done in a series of python scripts, starting with `parse.py` (parses the html file generated with curl script), `find_hops.py` (check descriptions from site for hop mentions), and `load_neo4j.py` (load DB).  Standard [ETL](https://en.wikipedia.org/wiki/Extract,_transform,_load) pattern I suppose. These can be executed together with `./run_py.sh`.  

Updating the database with new scrapes should merge nodes and relationships.  If you run into difficulties installing or running these scripts, feel welcome to open up an issue and I'll try to get back to you when I can.

## Example DB Queries

Some additional Neo4j cypher queries to help those not familiar with the [syntax](https://neo4j.com/developer/cypher/).

### Beers containing a hop (and their styles)

I claim these are among the most delicious.

```js
match p = (h:Hop)-[]-(b:Beer)-[]-(s:Style)
where h.name = 'Azacca'
return p
```

![azacca](img/azacca.svg)

### All beers of a particular style and their hop graph

```js
match p = (h:Hop)-[]-(b:Beer)-[]-(s:Style)
where s.style = 'Pale'
return p
```
![pales](img/pale_ales_hops.svg)

###  Beers with most unique hops

Neo4j query language supports json aggregations.  This example returns two beers with the largest numbers of found distinct hops as a single record containing the results aggregated as a json object.

```js
match (b:Beer)
with b.name as name,
    b.hops as hops, 
    b.description as description,
    size(b.hops) as num_hops
    order by num_hops DESC LIMIT 2
return collect({name : name, hops : hops, num_hops : num_hops, description : description }) as beers
```

```json
{
  "beers": [
    {
      "num_hops": 7,
      "name": "Alternative Facts IPA",
      "description": "No need for statistics, scientific research, data analysis, unbiased surveys/polls, experts in their field, or REALITY - your opinion is good enough for us! About this beer? We used 1.5 million pounds of Chinook, 522, Citra, Cascade, Amarillo, Mandarina, and Centennial hops - all of the best hops. The very best. Nobody builds better IPAs than us, it’s gonna be great, it’s gonna be YUGE…Fuuuuuuuck.",
      "hops": [
        "522",
        "Amarillo",
        "Cascade",
        "Centennial",
        "Chinook",
        "Citra",
        "Mandarina"
      ]
    },
    {
      "num_hops": 7,
      "name": "Rainfall IPA",
      "description": "Our friends from Portland, OR came up and things. Got. Juicy! We started with a base of PIlsner Malt, White Wheat, and Oats, added a whirlpool addition of Mosaic, Citra & Galaxy, and followed it up with  a massive dry-hop of Galaxy, Enigma, Vic Secret, Motueka, & Ella. The end result is a soft, balanced tropical downpour of haze!",
      "hops": [
        "Citra",
        "Ella",
        "Enigma",
        "Galaxy",
        "Mosaic",
        "Motueka",
        "Secret"
      ]
    }
  ]
}
```

###  Largest ABV beers

```js
match (b:Beer)
with b order by b.abv DESC limit 3
return collect({name : b.name, abv : b.abv, style : b.style}) as beers
```

```json
{
  "beers": [
    {
      "abv": 13.8,
      "name": "Barrel Aged Darkenfloxx",
      "style": "Fancy Beer"
    },
    {
      "abv": 11.9,
      "name": "Old Tubthumper",
      "style": "Fancy Beer"
    },
    {
      "abv": 11.8,
      "name": "Ixnay on the Islay",
      "style": "Fancy Beer"
    }
  ]
}
```

### Most frequent hop pairings

Find the most frequent hop pairings and alphabetized list of beer names containing said pairing

```js
match p = (a:Hop)-[]-(b:Beer)-[]-(c:Hop)
where a.name < c.name
with a,b,c order by b.name
with a.name as hop1, c.name as hop2, count(b) as freq, collect(b.name) as beer_list order by freq DESC limit 3
return collect({freq:freq, hop_pair : hop1 +' '+hop2, beer_list:beer_list}) as hop_pairs
```

This returns the following json (beer lists shown are truncated to fit better in this document).

```json
{
  "hop_pairs": [
    {
      "hop_pair": "Citra Mosaic",
      "freq": 51,
      "beer_list": [
        "A Whole New World",
        "Almost There IPA",
        "Art Deco Stuff",
        ...
      ]
    },
    {
      "hop_pair": "Citra Simcoe",
      "freq": 32,
      "beer_list": [
        "Brontosaurus Supernova",
        "Business or Pleasure? IPA",
        "Caller Unkown",
        ...
      ]
    },
    {
      "hop_pair": "Chinook Citra",
      "freq": 23,
      "beer_list": [
        "Alternative Facts IPA",
        "Change Of Plans",
        "Deadly Melody",
        ...
      ]
    }
  ]
}
```

## Neo4j Bloom

Neo4j Bloom is an enterprise UI that can run with locally on Neo4j Desktop (or Neo4j Enterprise if you're willing to pay for a server license).  Sorry Neo4j Community users.  It allows for the wrapping cypher queries with more human-usable phrases such as `find beers containing hop named Azacca`.  Target audience here is likely business users.

Example pictures are forthcoming.
