#!/usr/bin/env python

import json

from flask import Flask
from flask import render_template
app = Flask(__name__)

# Some fake data. Eventually this will come from CSV.
data = [
    {'freq': 150, 'size': 0.01},
    {'freq': 350, 'size': 0.1},
    {'freq': 50,  'size': 0.5},
    {'freq': 500, 'size': 1.0},
    {'freq': 200, 'size': 2.0},
  ]

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/data')
def ajax_data():
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True)
