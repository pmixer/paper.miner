from flask import Flask
from flask import jsonify
import json

# on how to start the APP:
# https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application

app = Flask(__name__)

# on how to return json data:
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view

@app.route('/neurips')
def hello_world():
    paper1 = {'title': 'paper1 title', 'year': 1987}
    paper2 = {'title': 'paper2 title', 'year': 1988}
    paper_list = [paper1, paper2]
    return jsonify(paper_list)
