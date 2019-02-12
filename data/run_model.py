import io
import json
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import sys

from coord_tools import coord_distance


# Function to calculate the proximity (in slope,sinuosity space) of two trails
def proximity(a,b):
	dx = a['slope'] - b['slope'] # Min-max ~1
	dy = a['sinuosity'] - b['sinuosity'] # Width ~1
	dz = (a['length'] - b['length']) / 2000.
	dv = (a['inflect'] - b['inflect']) / 15.
	dw = (a['spread'] - b['spread']) / 0.5
	return math.sqrt( dx*dx + dy*dy + dz*dz + dv*dv + dw*dw )

def modify( trail, feature, direction ):
	trail_new = trail.copy()
	if feature=='length':
		if direction=='down': trail_new['length'] -= 500
		elif direction=='up': trail_new['length'] += 500
	elif feature=='slope':
		if direction=='down': trail_new['slope'] -= 0.1
		elif direction=='up': trail_new['slope'] += 0.1
	elif feature=='spread':
		if direction=='down': trail_new['spread'] -= 0.1
		elif direction=='up': trail_new['spread'] += 0.1
	elif feature=='sinuosity':
		if direction=='down': trail_new['sinuosity'] -= 0.15
		elif direction=='up': trail_new['sinuosity'] += 0.15
	elif feature=='inflect':
		if direction=='down': trail_new['inflect'] -= 3.0
		elif direction=='up': trail_new['inflect'] += 3.0
	return trail_new


# Read json into dataframe
print('Loading data from json file...')
df = pd.read_json('data_processed.json')

# Transpose dataframe
df = df.T

# Pick out only the features of interest
df2 = df[['total_slope','sinuosity','total_length','inflect','slope_spread']]
df3 = df.copy(deep=True)

######################################################

# Output the data from our dataframe (and associated labels)
slope_dict = {}
count = 0
difficulty_mapper = {'easy':0, 'intermediate':1, 'advanced':2, 'expert':3}
colors = ['green','blue','black','gray']
difficulties = ['Easy','Intermediate','Advanced','Expert']

for i,row in df3.iterrows():
	nodeid = i
	# Not features
	name = df['name'][nodeid]
	rating = df['rating'][nodeid]
	resortname = df['resort_name'][nodeid]
	resortid = df['resort_id'][nodeid]
	state = df['state'][nodeid]
	last_coord = df['last_coord'][nodeid]
	max_slope = df['max_slope'][nodeid]
	# Features (and label)
	slope = row['total_slope']
	sinu  = row['sinuosity']
	length = row['total_length']
	inflect = row['inflect']
	spread = row['slope_spread']
	slope_dict[nodeid] = {'id':nodeid, 'name':name,
	                      'last_coord':last_coord, 'max_slope':max_slope,
	                      'rating':rating,'slope':slope, 'sinuosity':sinu,
	                      'length':length, 'inflect':inflect, 'spread':spread,
	                      'resort_name':resortname, 'resort_id':resortid, 'state':state}
	count += 1
	diff_level = difficulty_mapper[rating]


######################################################

# Loop back through our new dict of trails, and find a bunch of
#  neighbors for every trail. Also find trails that have some
#  feature shifted up or down
prox_nearest = []
prox_tenth = []
prox_random = []
trails_processed = 0
random.seed(3) # Use a fixed seed, for reproducibility
print('Finding nearest neighbors...')
for id in slope_dict.keys():
	randindex = random.choice( list(slope_dict.keys()) ) # Pick a random trail to compare against
	neighborhood_nat = []
	neighborhood_loc = []
	shifted_versions = {'length_up':modify(slope_dict[id], 'length', 'up'), # This trail with a feature shifted up or down
	           'length_down':modify(slope_dict[id], 'length', 'down'),
	           'slope_up':modify(slope_dict[id], 'slope', 'up'),
	           'slope_down':modify(slope_dict[id], 'slope', 'down'),
	           'spread_up':modify(slope_dict[id], 'spread', 'up'),
	           'spread_down':modify(slope_dict[id], 'spread', 'down'),
	           'sinu_up':modify(slope_dict[id], 'sinuosity', 'up'),
	           'sinu_down':modify(slope_dict[id], 'sinuosity', 'down'),
	           'inflect_up':modify(slope_dict[id], 'inflect', 'up'),
	           'inflect_down':modify(slope_dict[id], 'inflect', 'down')}
	best_shifted = {'length_up':[-999999,9], # Best matches to modified versions of this trail
	           'length_down':[-999999,9],
	           'slope_up':[-999999,9],
	           'slope_down':[-999999,9],
	           'spread_up':[-999999,9],
	           'spread_down':[-999999,9],
	           'sinu_up':[-999999,9],
	           'sinu_down':[-999999,9],
	           'inflect_up':[-999999,9],
	           'inflect_down':[-999999,9]}

	for jd in slope_dict.keys():
		if id == jd: continue
		prox = proximity(slope_dict[id], slope_dict[jd])
		if jd == randindex: prox_random.append(prox)
		if prox <= 0.5: # Find most similar slopes anywhere in the US
			neighborhood_nat.append( (jd,prox) )
		[lat1,lon1,elev1] = slope_dict[id]['last_coord']
		[lat2,lon2,elev2] = slope_dict[jd]['last_coord']
		dist = coord_distance(lat1,lon1,elev1,lat2,lon2,elev2)
		if dist < 100.*1600. and prox <= 0.5: # Find most similar slopes within 100 miles
			neighborhood_loc.append( (jd,prox,dist) )
		if prox < 0.75:
			for mod in shifted_versions.keys(): # Find most similar slopes with features shifted up/down
				prox_shifted = proximity(shifted_versions[mod], slope_dict[jd])
				if prox_shifted < best_shifted[mod][1]:
					best_shifted[mod][1] = prox_shifted
					best_shifted[mod][0] = jd
	neighborhood_nat.sort(key=lambda a: a[1])
	neighborhood_loc.sort(key=lambda a: a[1])
	slope_dict[id]['neighbors_usa'] = neighborhood_nat[:10]
	slope_dict[id]['neighbors_near'] = neighborhood_loc[:10]
	slope_dict[id]['shifted'] = best_shifted
	if len(neighborhood_nat) > 0:
		prox_nearest.append(slope_dict[id]['neighbors_usa'][0][1])
		prox_tenth.append(slope_dict[id]['neighbors_usa'][-1][1])
	trails_processed += 1
	if trails_processed %1000 == 0:
		print(f'Processed {trails_processed} trails so far...')

with open('labeled_results.json','w') as outfile:
	json.dump(slope_dict,outfile)
print('Wrote labeled data to labeled_results.json.')

n,bins,patches = plt.hist( x=prox_nearest, bins=np.linspace(0.,3.,30), color='green', alpha=0.5, label='Nearest trail')
n,bins,patches = plt.hist( x=prox_tenth, bins=np.linspace(0.,3.,30), color='blue', alpha=0.5, label='Tenth nearest')
n,bins,patches = plt.hist( x=prox_random, bins=np.linspace(0.,3.,30), color='red', alpha=0.5, label='Random trail')
plt.xlabel('Euclidean distance')
plt.ylabel('Trails')
plt.title('Proximity comparison')
plt.legend(loc='upper right')
plt.savefig('../figures/proximity_comparison.png')
print('Saved ../figures/proximity_comparison.png')
