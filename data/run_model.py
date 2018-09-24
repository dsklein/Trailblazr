import io
import json
import math
import numpy as np
import pandas as pd
import sys

# from sklearn.cluster import AffinityPropagation
# from sklearn import metrics
from sklearn.cluster import MeanShift, estimate_bandwidth


# Function to calculate the proximity (in slope,sinuosity space) of two trails
def proximity(a,b):
	dx = a['slope'] - b['slope']
	dy = a['sinuosity'] - b['sinuosity']
	return math.sqrt( dx*dx + dy*dy )


# Read json into dataframe
print('Loading data from json file...')
df = pd.read_json('data_processed.json')

# Transpose dataframe
df = df.T

# Pick out only the features of interest
df2 = df[['total_slope','sinuosity']]


# # Do the clustering using affinity propagation
# print('Running clustering...')
# af = AffinityPropagation(verbose=True).fit(df2)
# cluster_centers_indices = af.cluster_centers_indices_
# labels = af.labels_
# n_clusters_ = len(cluster_centers_indices)
# print(f'Found {n_clusters} clusters.')

# Estimate bandwidth and cluster using mean shift
print('Estimating bandwidth...')
bandwidth = estimate_bandwidth(df2, quantile=0.2, n_samples=6000, n_jobs=2)
print(f'Bandwidth chosen to be {bandwidth}.')
print('Running clustering...')
ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
# ^ Consider setting bin_seeding = True (will speed up bandwith finding)
# ^ Also consider setting min_bin_freq to some number > 1 (will only seed on higher bins)
ms.fit(df2)
labels = ms.labels_
cluster_centers = ms.cluster_centers_
labels_unique = np.unique(labels)
n_clusters_ = len(labels_unique)
print(f'Found {n_clusters_} clusters.')

print(cluster_centers)

############### Now do the plotting

import matplotlib.pyplot as plt
from itertools import cycle

plt.figure(1)
plt.clf()

colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
for k, col in zip(range(n_clusters_), colors):
    my_members = labels == k
    cluster_center = cluster_centers[k]
    print(f'Cluster {k} has {len(df2[my_members])} members.')
    print(f'\tCenter = ({cluster_center[0]},{cluster_center[1]})')
    plt.plot(df2[my_members]['total_slope'], df2[my_members]['sinuosity'], col + '.')
    plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)
plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.xlabel('Total Slope')
plt.ylabel('Sinuosity (adjusted)')
plt.savefig('../pictures/clusters.png')
print('Saved plot in ../pictures/clusters.png')
# plt.show()

# Output the data from our dataframe (and associated labels)
slope_dict = {}
count = 0
for i,row in df2.iterrows():
	nodeid = i
	name = df['name'][nodeid]
	rating = df['rating'][nodeid]
	slope = row['total_slope']
	sinu  = row['sinuosity']
	label = int(labels[count])
	# Somehow get nearest neighbors!
	slope_dict[nodeid] = {'id':nodeid, 'name':name, 'label':label,
	                      'rating':rating,'slope':slope, 'sinuosity':sinu}
	count += 1

# Loop back through our new dict of trails, and find a bunch of
#  neighbors for every trail
print('Finding nearest neighbors...')
for id in slope_dict.keys():
	neighborhood = []
	for jd in slope_dict.keys():
		if slope_dict[jd]['label'] != slope_dict[id]['label']: continue
		if id == jd: continue
		prox = proximity(slope_dict[id], slope_dict[jd])
		if prox > 0.05: continue
		neighborhood.append( (jd,prox) )
	neighborhood.sort(key=lambda a: a[1])
	slope_dict[id]['neighbors'] = neighborhood[:10]

with open('labeled_results.json','w') as outfile:
	json.dump(slope_dict,outfile)
print('Wrote labeled data to labeled_results.json.')
