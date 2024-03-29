import json

from neohelper import nh
from slugify import slugify


def create_beers(tx, file: str):

    """ Load from the results of cloudburst site scraper """

    with open(file, 'r') as f:
        beer_hops = json.load(f)
        beers = beer_hops['beers']

    # Slugify beer descriptions to better
    # string match with hop names, otherwise
    # we won't match hop names followed by
    # punctuation.
    for beer in beers:
        beer['slug_description'] = \
            slugify(beer['description'], separator=' ').title()

    query = """
        UNWIND $beers as beer
        MERGE (b:Beer {name : beer.beer_name,
            abv : beer.abv,
            style : beer.beer_style,
            description : beer.description
            })
        SET b.tmp_slug = beer.slug_description
        RETURN count(b) as c
        """
    records = tx.run(query, beers=beers)
    print(
        'Merged {} Beer nodes'
        .format(records.single()['c']))


def remove_beers_tmp_slug(tx):
    query = """
        MATCH (b:Beer)
        REMOVE b.tmp_slug
        """
    tx.run(query)


def create_hops(tx):

    """ Hops are loaded into the DB from multiple sources

    First is a hand-curated hop list to get better coverage
    of the cloudburst beer descriptions.  Contains names only.

    We also load from Yakima Chief, which makes nodes with
    additional data on aroma profiles and a useful description
    of the hop.
    """

    with open('data/hopnames.txt') as f:
        hoplist = f.read().splitlines()

    hoplist = [h.title() for h in hoplist if len(h) > 0]

    with open('data/yakimachiefhopdata.json', 'r') as f:
        ych = json.load(f)

    # This query is fast but definitely not idempotent
    query_params = []
    for i, hop in enumerate(ych['hops']):
        query_params.append([i, hop])

    query = """
        UNWIND $query_params as params
        MERGE (h:Hop { idx : params[0]})
        SET h += params[1]
        SET h.data_source = 'Yakima Chief'
        SET h.data_file = 'yakimachiefhopdata.json'
        """
    tx.run(query, query_params=query_params)

    query = """
        with $hoplist as hoplist
        UNWIND hoplist as name

        OPTIONAL MATCH (h:Hop {name:name})
        with h,name where h is NULL
        MERGE (new:Hop {name : name})
        SET new.data_source = 'Curated List'
        SET new.data_file = 'hopnames.txt'
        """
    tx.run(query, hoplist=hoplist)

    query = """
        match (n:Hop)
        return count(n) as c
    """
    records = tx.run(query)
    print("Merged {} Hop nodes".format(records.single()['c']))


def create_beer_contains_hop_edges(tx):

    query = """
        match (b:Beer)
        match (h:Hop)
        where b.tmp_slug contains h.name
        merge (b)-[e:CONTAINS]-(h)
        return count(e) as c
    """

    records = tx.run(query)
    print(
        'Merged {} (:Beer)-[:CONTAINS]-(:Hop) relationships'
        .format(records.single()['c']))


def create_styles(tx):
    query = """
        match (b:Beer)
        with distinct b.style as styles
        MERGE (s:Style {style : styles})
        with s
        match (b:Beer) where b.style = s.style
        MERGE (b)-[e:STYLE]->(s)
        return count(e) as c
        """
    records = tx.run(query)
    print(
        "Merged {} (:Beer)-[:STYLE]-(:Style) relationships"
        .format(records.single()['c']))


def create_hop_aromas(tx):

    query = """
        match (h:Hop)
        UNWIND h.aroma_profile as aromas
        with distinct aromas as aroma
        MERGE (a:Aroma {aroma : aroma})
        with a
        match (h:Hop) where a.aroma in h.aroma_profile
        MERGE (h)-[e:HAS_AROMA]-(a)
        return count(e) as c
        """
    records = tx.run(query)
    print(
        "Merged {} (:Hop)-[:HAS_AROMA]-(:Aroma) relationships"
        .format(records.single()['c']))


def style_abv_stats(tx):
    query = """
        match (s:Style)-[:STYLE]-(b:Beer)
        with s, avg(b.abv) as abv_mean, stDevP(b.abv) as abv_std
        set s.abv_mean = abv_mean
        set s.abv_std = abv_std
        """
    tx.run(query)
    print("Computed style mean/std abv.")

    query = """
        match (b:Beer)-[:STYLE]-(s:Style)
        set b.style_abv_z_score = (b.abv - s.abv_mean) / s.abv_std
    """
    tx.run(query)
    print("Computed beer style_abv_z_score")


if __name__ == '__main__':

    # Instantiate driver using evironmental variables
    nh.init_neo4j_driver("NEO4J_USER", "NEO4J_PW", "NEO4J_URI")
    driver = nh.get_driver()

    with driver.session() as session:
        swt = session.write_transaction
        swt(create_beers, 'data/beers.json')
        swt(create_hops)
        swt(create_beer_contains_hop_edges)
        swt(create_hop_aromas)
        swt(create_styles)
        swt(style_abv_stats)
        swt(remove_beers_tmp_slug)
    driver.close()
