from flask import Flask, render_template, request
import pandas as pd
import io,json

# This stuff is arbitrary python code
# df = pd.read_csv('https://data.boston.gov/dataset/c8b8ef8c-dd31-4e4e-bf19-af7e4e0d7f36/resource/29e74884-a777-4242-9fcc-c30aaaf3fb10/download/economic-indicators.csv',
#                  parse_dates=[['Year', 'Month']])
# length = len(df)

# list_of_trails = [
# 	{'id':'123','dispname':'Wimpy','cluster':'easy'},
# 	{'id':'456','dispname':"Murphy's Run",'cluster':'intermediate'},
# 	{'id':'789','dispname':'Hellbeast','cluster':'advanced'}
# 	]
with open('labeled_results.json','r') as infile:
	traildata = json.load(infile)
#myvar = 42

# This is a flask thing
app = Flask(__name__)


# This is where the magic happens
@app.route('/',methods=['POST','GET'])
def main():
	# Pass stuff to index.html
	# The names used in {{ }} are passed from here
	selected = ''
	message = 'This is a dummy message.'
	if request.method == 'GET':
		if 'trail' in request.args.keys():
			selected = request.args['trail']
		print('Someone used the GET method.')
		print(f'The trail is {selected}')
	# elif request.method == 'POST':
	# 	selected = request.form.get('trail')
	# 	print('Someone used the POST method.')
	# 	print(f'The trail is {selected}')
	# 	print(request)
	return render_template('index.html',
	                       #length=42, dataframe=df.to_html(),
	                       traillist=traildata,
	                       selected=selected)


if __name__ == '__main__':
    app.run(debug=True, port=5957)
