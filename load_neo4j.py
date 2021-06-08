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

    query = """
        UNWIND $beers as beer
        MERGE (b:Beer {name : beer.beer_name,
            abv : beer.abv,
            style : beer.beer_style,
            description : beer.description,
            hops : beer.hops
        })
        RETURN count(b) as c
        """
    records = tx.run(query, beers = beers)
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

    swt = session.write_transaction

    propindex = {'Beer':'name',
        'Hop':'name',
        'Style':'style',
        }

    for label, prop in propindex.items():
        swt(create_property_index, label, prop)

    index_name = 'titlesAndDescriptions'
    nodes = ['Beer']
    properties = ['name', 'description']

    # Fun fact - Neo4j's query to check indexes is
    # rejected if run as a read transaction. Mkay.
    if not swt(index_exists,index_name):
        swt(create_fulltext_index,index_name, nodes, properties)

    swt(print_db_indexes) 


def create_property_index(tx,label,prop):
    query = """
        CREATE INDEX {} IF NOT EXISTS FOR (n:{}) ON (n.{})
        """.format(label+'_'+prop, label, prop)
    tx.run(query)        

def index_exists(tx,index_name):
    """ Check for index existence to prevent throwing
    exceptions in the code.
    """

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

def load_yakima_chief_ontology(tx):
    with open(os.path.join('yakima-chief-hop-parse',
        'yakimachiefhopdata.json'),'r') as f:
        ych = json.load(f)
    print(json.dumps(ych,indent=2))

    print(ych['hops'][2])
    query_params = []
    for i,hop in enumerate(ych['hops']):
        query_params.append([i,hop])
    
    query = """
        UNWIND $query_params as params
        MERGE (b:YC_Hop { idx : params[0]})
        SET b += params[1]
        RETURN count(b) as c
        """

    records = tx.run(query, query_params = query_params)
    print('Merged {} YC_Hop nodes'
        .format(records.single()['c']))

    query = """
        match (b:YC_Hop)
        UNWIND b.styles as styles
        with distinct styles as style
        MERGE (s:YC_Style {style : style})
        with s
        match (b:YC_Hop) where s.style in b.styles
        MERGE (b)-[e:RECOMMENDED]-(s)
        return count(e) as c
        """
    records = tx.run(query)
    print("Merged {} (:YC_Hop)-[:RECOMMENDED]-(:YC_Style) relationships"
        .format(records.single()['c']))

    query = """
        match (b:YC_Hop)
        UNWIND b.aroma_profile as aromas
        with distinct aromas as aroma
        MERGE (s:YC_Aroma {aroma : aroma})
        with s
        match (b:YC_Hop) where s.aroma in b.aroma_profile
        MERGE (b)-[e:HAS_AROMA]-(s)
        return count(e) as c
        """
    records = tx.run(query)
    print("Merged {} (:YC_Hop)-[:RECOMMENDED]-(:YC_Style) relationships"
        .format(records.single()['c']))


if __name__ == '__main__':

    uri = "neo4j://localhost:7687"

    try:
        pw = os.environ['NEO4J_PW']
    except KeyError as e:
        msg = "No environment variable `NEO4J_PW` found.  Consider running export NEO4J_PW='yourpassword' in the current shell environment or in your shell config file."
        raise KeyError(msg)
        

    driver = GraphDatabase.driver(uri, auth=("neo4j", pw))

    with driver.session() as session:
        swt = session.write_transaction
        swt(create_hops)
        swt(create_beers)
        swt(create_contains_hop_edges)
        swt(create_styles)
        swt(load_yakima_chief_ontology)
        create_indexes(session)
    driver.close()
