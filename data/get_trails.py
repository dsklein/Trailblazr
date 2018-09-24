import io
import json
import overpass

# Initialize overpass API object
api = overpass.API(timeout=600)

# Form and send the overpass query
print('Querying Overpass API...')
result = api.get("""
area["name"="United States"]->.boundaryarea;
(
way(area.boundaryarea)["piste:type"="downhill"];
>;
);
""", verbosity='body', responseformat='json')
print('...done!')

# A little helpful output...
print(f"Received {len(result['elements'])} elements.")

# Write the received json to a file
print('Writing json data to file.')
with open('data_usa.json','w') as outfile:
	json.dump(result,outfile)

# Blah Blah
