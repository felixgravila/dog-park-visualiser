#%%

from bs4 import BeautifulSoup

import json
import os
import re

htmldir = "./webpages"
htmlfiles = [os.path.join(htmldir, f) for f in os.listdir(htmldir)]

# %%

def get_dogparks_for_file(file):

    area = file.split("/")[-1].split("_")[0]

    with open(file, "r") as f:
        filecontent = f.read()
    soup = BeautifulSoup(filecontent, "html.parser")

    dogparks = []

    content_box = soup.find(id="content_box")
    for parkcard in content_box.find_all("article", {"class": ["latestPost", "excerpt", "article", "clearfix"]}):
        park_name = parkcard.find("h1", {"class": "entry-title"}).find("a").attrs['title']
        park_addr = parkcard.find("p", {"class": "rc_address"}).text.replace("Adresse: ", "")
        gps, parking, indhegnet = None, None, None
        for res in [p.text.strip() for p in parkcard.find_all("p", {"class": "rc_gps"})]:
            if res.startswith("GPS:"):
                gps = res
            elif res.startswith("Parkering GPS:"):
                parking = res
            elif res.startswith("Indhegnet:"):
                indhegnet = res
            else:
                print(res)

        coord_pattern = re.compile('\d+\.\d+')
        if gps:
            main_lat, main_lon = list(map(float, coord_pattern.findall(gps)))
        if parking:
            park_lat, park_lon = list(map(float, coord_pattern.findall(parking)))

        fenced = "Indhegnet:\n                    Ja" in indhegnet

        dogpark_obj = {
            "name": park_name,
            "addr": park_addr,
            "fenced": fenced,
            "area": area
        }

        if gps:
            dogpark_obj['gps'] = {
                "lat": main_lat,
                "lon": main_lon
            }
        if parking:
            dogpark_obj['parking_gps'] = {
                "lat": park_lat,
                "lon": park_lon
            }

        dogparks.append(dogpark_obj)

    return dogparks

dogparks = []
for f in htmlfiles:
    dogparks.extend(get_dogparks_for_file(f))

with open("dogparks.json", "w") as f:
    json.dump(dogparks, f, indent=2)


# %%

