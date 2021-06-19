from flask import Flask, render_template
from views.api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5050)
else:
    print('Please run from main.py')
