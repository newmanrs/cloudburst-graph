import json
import re

with open('hoplist.txt','r') as f:
    hops = f.readlines();
hops = [hop.lower().strip() for hop in hops]
hopset = set(hops)

with open('tmp/beers.json') as f:
    beers = json.load(f)
beer_list = beers['beers'];

for beer in beer_list:
    print('\n')
    print(beer['beer_name'])
    print(beer['description'])
    desc = ''.join(i if i.isalnum() else ' ' for i in beer['description'])
    desc = desc.lower().split(' ');
    descset = set(desc)
    setint = hopset.intersection(descset)
    if len(setint) > 0:
        beer['hops'] = sorted([h.capitalize() for h in setint])

with open('tmp/beers_hops.json', 'w') as f:
    json.dump({'beers' : beer_list}, f, indent = 2);
