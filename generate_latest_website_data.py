import json
import random

from clean_waimapihi.read_sheets_data import get_latest_data
from clean_waimapihi.clean_sightings import clean_data, add_coords
from clean_waimapihi.df_wrangler import DFWrangler


values = get_latest_data()

df = clean_data(values)
df = add_coords(df)

wrangler = DFWrangler(df)
latest_bird_data = wrangler.summary_data()

path = '../toutouwai/scripts/data.js'

with open(path, 'r') as f:
    website_data = {bird["band"]: bird for bird in json.loads(f.read().replace('data =', ''))}

def wiggle_lat_long(loc):
    return loc + random.randint(-10, 10) * 0.00001

new_website_data = []

for bird in latest_bird_data.to_dict("records"):
    existing_record = website_data.get(bird["band"], {})
    record = {'band': bird["band"],
    'sex': existing_record.get("sex", "Unknown"),
    'territory': {'text': bird["territory_name"],
  'lat': wiggle_lat_long(bird["lat"]),
  'lng': wiggle_lat_long(bird["lng"])},
 'banded': bird["first_seen"],
 'confirmed_missing': bird["last_seen"] if bird["is_missing"] else "",
 'description': existing_record.get("description", ""),
 'images': existing_record.get("images", [])}
    new_website_data.append(record)

with open(path, 'w') as f:
    f.write("data = " + json.dumps(new_website_data, indent=4))