import io
import json
import numpy as np
import matplotlib.pyplot as plot
import sys
import time

from statsmodels.distributions.empirical_distribution import ECDF


# First command-line argument is the file to open.
# If no file is specified, use the usa data as a default
filename = 'data_processed.json'
if len(sys.argv) == 2:
	filename = sys.argv[1]
elif len(sys.argv) > 2:
	print('Too many arguments specified! Exiting...')
	exit()

# Open the data file
with open(filename,'r') as infile:
	data = json.load(infile)

# Count the entries
num_trails = len(data.keys())
print(f'Found {num_trails} trails.')
if num_trails == 0:
	print('File has no trails. Exiting...')
	exit()

# These will hold the data to make 1D histograms
histlist_horizlength = [[],[],[],[]]
histlist_totallength = [[],[],[],[]]
histlist_totalslope = [[],[],[],[]]
histlist_maxslope = [[],[],[],[]]
histlist_minslope = [[],[],[],[]]
histlist_slopespread = [[],[],[],[]]
histlist_sinuosity = [[],[],[],[]]
histlist_inflect = [[],[],[],[]]


# Loop over the entries
print('Running looper...')
for trail in data.keys():

	# Use a numerical shortcut for the existing difficulty rating
	idx=-99
	if   data[trail]['rating'] == 'easy': idx=0
	elif data[trail]['rating'] == 'intermediate': idx=1
	elif data[trail]['rating'] == 'advanced': idx=2
	elif data[trail]['rating'] == 'expert':idx=3

	# populate lists to be made into histograms
	histlist_horizlength[idx].append( data[trail]['horiz_length'] )
	histlist_totallength[idx].append( data[trail]['total_length'] )
	histlist_totalslope[idx].append( data[trail]['total_slope'] )
	histlist_maxslope[idx].append( data[trail]['max_slope'] )
	histlist_minslope[idx].append( data[trail]['min_slope'] )
	histlist_slopespread[idx].append( data[trail]['slope_spread'] )
	histlist_sinuosity[idx].append( data[trail]['sinuosity'] )
	histlist_inflect[idx].append( data[trail]['inflect'] )

	
# end of loop over trails
labels = ['Easy','Intermediate','Advanced','Expert']
colors = ['green','blue','black','gray']
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_horizlength, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Length (meters)')
plot.ylabel('Trails')
plot.title('Horizontal trail length')
plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/horiz_length.png')
print('Saved ../figures/horiz_length.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_totallength, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Length (meters)')
plot.ylabel('Trails')
plot.title('Total trail length')
plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/total_length.png')
print('Saved ../figures/total_length.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_totalslope, bins=np.linspace(0.,1.,41), stacked='true', color=colors, label=labels)
plot.xlabel('Slope (rise/run)')
plot.ylabel('Trails')
plot.title('Overall slope')
#plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/total_slope.png')
print('Saved ../figures/total_slope.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_maxslope, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Slope')
plot.ylabel('Trails')
plot.title('Max trail slope')
#plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/max_slope.png')
print('Saved ../figures/max_slope.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_minslope, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Slope')
plot.ylabel('Trails')
plot.title('Min trail slope')
#plot.yscale('log')
plot.legend(loc='upper left')
# plot.show()
plot.savefig('../figures/min_slope.png')
print('Saved ../figures/min_slope.png')
plot.clf()
time.sleep(0.2)
	
n,bins,patches = plot.hist(x=histlist_sinuosity, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Curvature (length / straight distance)')
plot.ylabel('Trails')
plot.title('Curvature')
plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/sinuosity.png')
print('Saved ../figures/sinuosity.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_inflect, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Turns per km')
plot.ylabel('Trails')
plot.title('Changes of direction')
# plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/inflect.png')
print('Saved ../figures/inflect.png')
plot.clf()
time.sleep(0.2)

n,bins,patches = plot.hist(x=histlist_slopespread, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('(Max - Min) Slope')
plot.ylabel('Trails')
plot.title('Slope spread')
# plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/slopespread.png')
print('Saved ../figures/slopespread.png')
plot.clf()
time.sleep(0.2)

###################################33
## Make some 2D plots

#fig,ax = plot.subplots()
for i in range(0,4):
	plot.scatter(histlist_totalslope[i],histlist_sinuosity[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total Slope')
plot.ylabel('Curvature')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../figures/sinuosity_vs_totalslope.png')
print('Saved ../figures/sinuosity_vs_totalslope.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_maxslope[i],histlist_sinuosity[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Max Slope')
plot.ylabel('Curvature')
plot.legend()
# plot.show()
plot.savefig('../figures/sinuosity_vs_maxslope.png')
print('Saved ../figures/sinuosity_vs_maxslope.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_totalslope[i],histlist_maxslope[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total Slope')
plot.ylabel('Max Slope')
plot.legend()
# plot.show()
plot.savefig('../figures/maxslope_vs_totalslope.png')
print('Saved ../figures/maxslope_vs_totalslope.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_totalslope[i],histlist_totallength[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total Slope')
plot.ylabel('Total length')
plot.legend()
# plot.show()
plot.savefig('../figures/totallength_vs_totalslope.png')
print('Saved ../figures/totallength_vs_totalslope.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_sinuosity[i],histlist_totallength[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Curvature')
plot.ylabel('Total length')
plot.legend()
# plot.show()
plot.savefig('../figures/totallength_vs_sinuosity.png')
print('Saved ../figures/totallength_vs_sinuosity.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_sinuosity[i],histlist_inflect[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Curvature')
plot.ylabel('Turns per km')
plot.legend()
# plot.show()
plot.savefig('../figures/inflect_vs_sinuosity.png')
print('Saved ../figures/inflect_vs_sinuosity.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_totallength[i],histlist_inflect[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total length')
plot.ylabel('Turns per km')
plot.legend()
# plot.show()
plot.savefig('../figures/inflect_vs_totallength.png')
print('Saved ../figures/inflect_vs_totallength.png')
plot.clf()
time.sleep(0.2)

for i in range(0,4):
	plot.scatter(histlist_totalslope[i],histlist_slopespread[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total slope')
plot.ylabel('Slope spread')
plot.legend()
# plot.show()
plot.savefig('../figures/slopespread_vs_totalslope.png')
print('Saved ../figures/slopespread_vs_totalslope.png')
plot.clf()
time.sleep(0.2)


###################################
#  Make some ECDF plots

featuredata = [histlist_horizlength, histlist_totallength, histlist_totalslope, histlist_maxslope, histlist_minslope, histlist_slopespread, histlist_sinuosity, histlist_inflect]
variable = ['horizlength', 'totallength', 'totalslope', 'maxslope', 'minslope', 'slopespread', 'sinuosity', 'inflect']
varname = ['Horizontal Length', 'Total Length', 'Total Slope', 'Max Slope', 'Min Slope', 'Slope Spread', 'Curvature', 'Turns per km']

for featurelist, var, name in zip(featuredata,variable,varname):
	for i in range(0,4):
		ecdf = ECDF( featurelist[i] )
		plot.plot( ecdf.x, ecdf.y, color=colors[i], label=labels[i] )
	plot.xlabel(name)
	plot.ylabel('Cumulative probability')
	plot.title('ECDF:'+name)
	plot.legend(loc='lower right')
	# plot.show()
	plot.savefig('../figures/ECDF_'+var+'.png')
	print('Saved ../figures/ECDF_'+var+'.png')
	plot.clf()
	time.sleep(0.2)
# Done looping over variables
