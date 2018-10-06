from flask import Flask, render_template, request
#import pandas as pd
import io,json

# This stuff is arbitrary python code

# Import trail data
with open('labeled_results.json','r') as infile:
	traildata = json.load(infile)

# Generate a list of resorts/mountains
resort_list = {}
for trail in traildata.keys():
	resort_id = traildata[trail]['resort_id']
	if resort_id not in resort_list.keys():
		resort_list[resort_id] = {'name':traildata[trail]['resort_name'], 'state':traildata[trail]['state']}
	elif resort_list[resort_id]['state'] == 'UNKNOWN':
		resort_list[resort_id]['state'] = traildata[trail]['state']
	# Keys are of type 'int'

# Generate list of resort ids/names, sorted by resort name
resorts = [(id,resort_list[id]['name']) for id in resort_list.keys()]
resorts_sorted = sorted( resorts, key=lambda t: t[1])

# Generate list of trail ids/names, sorted by trail name
trails = [(id,traildata[id]['name']) for id in traildata.keys()]
trails_sorted = sorted( trails, key=lambda t: t[1])

# This is a flask thing
app = Flask(__name__)


# This is where the magic happens
@app.route('/',methods=['POST','GET'])
def main():
	selected_trail = ''
	selected_resort = 0
	if request.method == 'GET':
		#print('\nSomeone used the GET method.')
		#print(request)
		if 'trail' in request.args.keys():
			selected_trail = request.args['trail']
			if selected_trail not in traildata.keys(): selected_trail = ''
		if 'resort' in request.args.keys():
			try:
				selected_resort = int(request.args['resort'])
			except ValueError:
				selected_resort = 0
			if selected_resort not in resort_list.keys(): selected_resort = 0
		#print(f'The trail is {selected_trail}')
		if selected_resort != 0:
			#print(f'The resort is {resort_list[selected_resort]}')
			if selected_trail != '' and traildata[selected_trail]['resort_id'] != selected_resort:
				selected_trail =  ''
				#print('Resetting selected trail.')

	# Pass stuff to index.html
	# The names used in {{ }} are passed from here
	return render_template('index.html',
	                       traillist=traildata, selectedtrail=selected_trail,
	                       resortlist=resort_list, selectedresort=selected_resort,
	                       resortsbyname=resorts_sorted, trailsbyname=trails_sorted)


if __name__ == '__main__':
    app.run(debug=True, port=5957)
