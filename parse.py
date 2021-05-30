from bs4 import BeautifulSoup
import json
import re
with open('tmp/cb.html','r') as f:
    contents = f.read()
    soup = BeautifulSoup(contents,'html.parser')

beer_list = []
beers = soup.find_all('button','cb-beer-button')

for i, beer in enumerate(beers):

    #Extract data
    b = dict()
    b['beer_name'] = beer.find("h3","cb-beer-title").text

    #consider saving the container element for all beers, and not using the raw soup of entire file here - all file scan in this loop is by far the slowest step here.
    s = 'cb-beer-modal-'+str(i+1);
    beer = soup.find('div', id = s)
    b['beer_style'] = beer.find("span","cb-beer-style").text
    b['abv'] = beer.find("span", "cb-beer-abv").text

    if ibu:= beer.find("span","cb-beer-ibu"):
        b['ibu'] = ibu.text.split(" ")[0]


    #Extract description - just be wary format of adding title, ibu, and abv data
    # is not uniform for all entries.
    des = beer.text
    des = re.split('\t|\n',des);
    b['description'] = max(des,key=len)


    #Trim % off abv
    b['abv'] = float(b['abv'][0:-1])
    beer_list.append(b)

#with open('hoplist.txt','r') as f:
#    hops = f.readlines();

#for beer in beer_list:
#    desc = beer['description'].lower().split(' ');
#    print(desc)

with open('tmp/beers.json','w') as f:
    json.dump({'beers': beer_list}, f, indent=2)
