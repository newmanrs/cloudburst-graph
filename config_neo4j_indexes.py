from neo4j import GraphDatabase
import json
import os
from neohelper.utils import init_neo4j_driver


def create_indexes(session):

    swt = session.write_transaction

    # B-tree single property indexes
    propindex = {
        'Beer': 'name',
        'Hop': 'name',
        'Style': 'style',
        'Aroma': 'aroma',
        }

    for label, prop in propindex.items():
        swt(create_property_index, label, prop)

    index_name = 'name_and_description'
    nodes = ['Beer', 'Hop']
    properties = ['name', 'description']

    # Fun fact - Neo4j's query to check indexes is
    # rejected if run as a read transaction. Mkay.
    if not swt(index_exists, index_name):
        swt(create_fulltext_index, index_name, nodes, properties)

    swt(print_db_indexes)


def create_property_index(tx, label, prop):
    query = """
        CREATE INDEX {} IF NOT EXISTS FOR (n:{}) ON (n.{})
        """.format(label+'_'+prop, label, prop)
    tx.run(query)


def index_exists(tx, index_name):
    """ Check for index existence to prevent throwing
    exceptions in the code.
    """

    records = tx.run("SHOW INDEXES")
    for r in records:
        if index_name in r['name']:
            return True
    return False


def create_fulltext_index(tx, name, nodes, properties):

    query = """
        CALL db.index.fulltext.createNodeIndex('{}', {}, {})
        """.format(name, nodes, properties)
    tx.run(query)


def print_db_indexes(tx):

    records = tx.run('SHOW INDEXES')
    for i, r in enumerate(records):
        if i == 0:
            print("Database Indexes")
        d = dict(r)
        print(" Index Name '{}'".format(d['name']))
        del d['name']
        s = json.dumps(d, indent=None)
        lines = s.splitlines(keepends=True)
        print(''.join(['  ' + l for l in lines]))


if __name__ == '__main__':

    # Instantiate driver using evironmental variables
    driver = init_neo4j_driver("NEO4J_USER", "NEO4J_PW", "NEO4J_URI")

    with driver.session() as session:
        create_indexes(session)
    driver.close()
