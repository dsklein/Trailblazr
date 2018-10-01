from flask import Flask, render_template, request
import pandas as pd
import io,json

# This stuff is arbitrary python code

with open('labeled_results.json','r') as infile:
	traildata = json.load(infile)

resort_list = {}
for trail in traildata.keys():
	resort_id = traildata[trail]['resort_id']
	if resort_id not in resort_list.keys():
		resort_list[resort_id] = {'name':traildata[trail]['resort_name'], 'state':traildata[trail]['state']}
	elif resort_list[resort_id]['state'] == 'UNKNOWN':
		resort_list[resort_id]['state'] = traildata[trail]['state']
	# Keys are of type 'int'

# This is a flask thing
app = Flask(__name__)


# This is where the magic happens
@app.route('/',methods=['POST','GET'])
def main():
	selected_trail = ''
	selected_resort = 0
	# Pass stuff to index.html
	# The names used in {{ }} are passed from here
	if request.method == 'GET':
		print('\nSomeone used the GET method.')
		print(request)
		if 'trail' in request.args.keys():
			selected_trail = request.args['trail']
		if 'resort' in request.args.keys():
			selected_resort = int(request.args['resort'])
		print(f'The trail is {selected_trail}')
		if selected_resort != 0:
			print(f'The resort is {resort_list[selected_resort]}')
			if selected_trail != '' and traildata[selected_trail]['resort_id'] != selected_resort:
				selected_trail =  ''
				print('Resetting selected trail.')
	# elif request.method == 'POST':
	# 	selected_resort = request.form.get('resort')
	# 	print('\nSomeone used the POST method.')
	# 	print(f'The resort is {resort_list[int(selected_resort)]}')
	# 	print(f'The trail is {selected_trail}')
	# 	selected_trail = '' # If the user just selected a resort, clear saved trail
	return render_template('index.html',
	                       traillist=traildata, selectedtrail=selected_trail,
	                       resortlist=resort_list, selectedresort=selected_resort)


if __name__ == '__main__':
    app.run(debug=True, port=5957)
