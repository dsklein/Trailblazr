import io
import json
import overpass

# Initialize overpass API object
api = overpass.API(timeout=600)

# Form and send the overpass query
print('Querying Overpass API...')
# Looking for all ski areas/mountains/resorts within 200m of a ski trail
result = api.get("""
area["name"="United States"]->.boundaryarea;
(
way(area.boundaryarea)["piste:type"="downhill"];
)->.trails;
(
	node(around.trails:200)["leisure"="sports_centre"];
	node(around.trails:200)["site"="piste"];
  	node(around.trails:200)["name"~"ski",i];
  	node(around.trails:200)["name"~"resort",i];
  	node(around.trails:200)["name"~"valley",i];
  	node(around.trails:200)["name"~"mountain",i];
  	node(around.trails:200)["name"~"peak",i];
);
""", verbosity='body', responseformat='json')
print('...done!')

# A little helpful output...
print(f"Received {len(result['elements'])} elements.")

# Write the received json to a file
print('Writing json data to file.')
with open('data_resorts.json','w') as outfile:
	json.dump(result,outfile)

# End of file
