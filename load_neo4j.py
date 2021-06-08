from neo4j import GraphDatabase
import neo4j
import json
import os

def create_hops(tx):

    with open('hoplist.txt') as f:
        hoplist = f.read().splitlines();

    #remove empty strings
    hoplist = [h.capitalize() for h in hoplist if len(h) > 0]
    hoplist = sorted(hoplist)

    query = """
        with $hoplist as hoplist
        UNWIND hoplist as hopname
        MERGE (h:Hop {name : hopname})
        return count(h) as hops
        """
    records = tx.run(query,hoplist=hoplist)
    print("Merged {} Hop nodes"
        .format(records.single()['hops']))


def create_beers(tx):

    with open('tmp/beers_hops.json', 'r') as f:
        beer_hops = json.load(f)
        beers = beer_hops['beers']

    # Consider making this property optional
    for beer in beers:
        if not 'hops' in beer:
            beer['hops'] = ['unknown']

    query2 = """
        UNWIND $beers as beer
        MERGE (b:Beer {name : beer.beer_name,
            abv : beer.abv,
            style : beer.beer_style,
            description : beer.description,
            hops : beer.hops
        })
        RETURN count(b) as c
        """
    records = tx.run(query2, beers = beers)
    print('Merged {} Beer nodes'
        .format(records.single()['c']))

def create_contains_hop_edges(tx):
    query = """
        match (h:Hop)
        with h
        match (b:Beer) where h.name in b.hops
        MERGE (b)-[e:CONTAINS]-(h)
        return count(e) as c
        """
    records = tx.run(query)
    print('Merged {} (:Beer)-[:CONTAINS]-(:Hop) relationships'
        .format(records.single()['c']))

def create_styles(tx):
    query = """
        match (b:Beer)
        with distinct b.style as styles
        MERGE (s:Style {style : styles})
        with s
        match (b:Beer) where b.style = s.style
        MERGE (b)-[e:STYLE]-(s)
        return count(e) as c
        """
    records = tx.run(query)
    print("Merged {} (:Beer)-[:STYLE]-(:Style) relationships"
        .format(records.single()['c']))

def create_indexes(session):

    wt = session.write_transaction
    propindex = {'Beer':'name',
        'Hop':'name',
        'Style':'style',
        }

    for label, prop in propindex.items():
        wt(create_property_index, label, prop)

    index_name = 'titlesAndDescriptions'
    nodes = ['Beer']
    properties = ['name', 'description']

    if not wt(index_exists,index_name):
        wt(create_fulltext_index,index_name, nodes, properties)

    wt(print_db_indexes) 


def create_property_index(tx,label,prop):
    query = """
        CREATE INDEX {} IF NOT EXISTS FOR (n:{}) ON (n.{})
        """.format(label+'_'+prop, label, prop)
    tx.run(query)        

def index_exists(tx,index_name):

    records = tx.run("SHOW INDEXES")
    for r in records:
        if index_name in r['name']:
            return True
    return False        


def create_fulltext_index(tx,name,nodes,properties):

    name = 'titlesAndDescriptions'
    nodes = ['Beer']
    properties = ['name', 'description']

    query = """
        CALL db.index.fulltext.createNodeIndex('{}', {}, {})
        """.format(name,nodes,properties)
    tx.run(query)

def print_db_indexes(tx):

    records = tx.run('SHOW INDEXES')
    for i,r in enumerate(records):
        if i == 0:
            print("Database Indexes")
        d = dict(r)
        print(" Index Name '{}'".format(d['name']))
        del d['name']
        s = json.dumps(d,indent=2)
        lines = s.splitlines(keepends=True)
        print(''.join(['  '+l for l in lines]))
    

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
        create_indexes(session)
    driver.close()
