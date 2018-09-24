import io
import json
import matplotlib.pyplot as plot
import sys


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
histlist_totalslope = [[],[],[],[]]
histlist_steepestslope = [[],[],[],[]]
histlist_flattestslope = [[],[],[],[]]
histlist_maxupslope = [[],[],[],[]]
histlist_sinuosity = [[],[],[],[]]

# Can also make 2D scatterplots
# BLAH
# BLAH


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
	histlist_totalslope[idx].append( data[trail]['total_slope'] )
	histlist_steepestslope[idx].append( data[trail]['steepest_slope'] )
	histlist_flattestslope[idx].append( data[trail]['flattest_slope'] )
	histlist_maxupslope[idx].append( data[trail]['max_up_slope'] )
	histlist_sinuosity[idx].append( data[trail]['sinuosity'] )

	# Populate list pairs to make scatterplots
	# blah
	# blah
	
# end of loop over trails
labels = ['Easy','Intermediate','Advanced','Expert']
colors = ['green','blue','black','gray']

n,bins,patches = plot.hist(x=histlist_horizlength, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Distance (meters)')
plot.ylabel('Trails')
plot.title('Horizontal trail length')
plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../pictures/horiz_length.png')
print('Saved ../pictures/horiz_length.png')
plot.clf()

n,bins,patches = plot.hist(x=histlist_totalslope, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Slope')
plot.ylabel('Trails')
plot.title('Trail total slope')
#plot.yscale('log')
plot.legend(loc='upper left')
# plot.show()
plot.savefig('../pictures/total_slope.png')
print('Saved ../pictures/total_slope.png')
plot.clf()

n,bins,patches = plot.hist(x=histlist_steepestslope, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Slope')
plot.ylabel('Trails')
plot.title('Steepest trail slope')
#plot.yscale('log')
plot.legend(loc='upper left')
# plot.show()
plot.savefig('../pictures/steepest_slope.png')
print('Saved ../pictures/steepest_slope.png')
plot.clf()

# n,bins,patches = plot.hist(x=histlist_flattestslope, bins='auto', stacked='true', color=colors, label=labels)
# plot.xlabel('Slope')
# plot.ylabel('Trails')
# plot.title('Flattest trail slope')
# # plot.yscale('log')
# # plot.show()
# plot.savefig('../pictures/flattest_slope.png')
# print('Saved ../pictures/flattest_slope.png')

n,bins,patches = plot.hist(x=histlist_maxupslope, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Slope')
plot.ylabel('Trails')
plot.title('Steepest upward slope')
#plot.yscale('log')
plot.legend(loc='upper right')
# plot.show()
plot.savefig('../pictures/max_up_slope.png')
print('Saved ../pictures/max_up_slope.png')
plot.clf()
	
n,bins,patches = plot.hist(x=histlist_sinuosity, bins='auto', stacked='true', color=colors, label=labels)
plot.xlabel('Sinuosity')
plot.ylabel('Trails')
plot.title('Sinuosity')
plot.yscale('log')
plot.legend(loc='upper right')
plot.show()
plot.savefig('../pictures/sinuosity.png')
print('Saved ../pictures/sinuosity.png')
plot.clf()

#fig,ax = plot.subplots()
for i in range(0,4):
	plot.scatter(histlist_totalslope[i],histlist_sinuosity[i],c=colors[i],alpha=0.2,label=labels[i])
plot.xlabel('Total Slope')
plot.ylabel('Sinuosity')
plot.legend()
# plot.show()
plot.savefig('../pictures/sinuosity_vs_totalslope.png')
print('Saved ../pictures/sinuosity_vs_totalslope.png')
