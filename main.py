from flask import Flask, render_template
from views.api import api

import os

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return render_template('home.html')

#if __name__ == '__main__':
def app():
    app.run(debug=True, port=os.getenv('PORT'))
#else:
#    print('Please run from main.py')
