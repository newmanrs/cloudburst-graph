from neo4j import GraphDatabase
import json
import os

def create_hops(tx):
    with open('hoplist.txt') as f:
        hoplist = f.read().splitlines();

    #remove empty strings
    hoplist = [h.capitalize() for h in hoplist if len(h) > 0]
    hoplist = sorted(hoplist)

    query = """
        MERGE (h:Hop {name : $name})
        """
    for name in hoplist:
        tx.run(query,name=name);

def create_beers(tx):
    with open('tmp/beers_hops.json', 'r') as f:
        beer_hops = json.load(f)
        beers = beer_hops['beers']

    query = """
        MERGE (b:Beer {name : $name,
        abv : $abv,
        style : $style,
        description : $description,
        hops : $hops
        })
        """

    for beer in beers:
        if not 'hops' in beer:
            beer['hops'] = ['unknown']

        tx.run(query,name=beer['beer_name'], abv=beer['abv'], description = beer['description'], hops = beer['hops'], style = beer['beer_style'])

def create_contains_hop_edges(tx):
    query = """
        match (h:Hop)
        with h
        match (b:Beer) where h.name in b.hops
        MERGE (b)-[:CONTAINS]-(h)
        """
    tx.run(query)

def create_styles(tx):
    query = """
        match (b:Beer)
        with distinct b.style as styles
        MERGE (s:Style {style : styles})
        with s
        match (b:Beer) where b.style = s.style
        MERGE (b)-[:STYLE]-(s)
        """
    tx.run(query)

if __name__ == '__main__':

    uri = "neo4j://localhost:7687"

    try:
        pw = os.environ['NEO4J_PW']
    except KeyError as e:
        msg = "No environment variable `NEO4J_PW` found.  Consider running export NEO4J_PW='yourpassword' in the current shell environment or in your shell config file."
        raise KeyError(msg)
        

    driver = GraphDatabase.driver(uri, auth=("neo4j", pw))

    with driver.session() as session:
        session.write_transaction(create_hops)
        session.write_transaction(create_beers)
        session.write_transaction(create_contains_hop_edges)
        session.write_transaction(create_styles)
    driver.close()
