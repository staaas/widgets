import json

from flask import Flask
from fbgroup import facebook_group_widget


app = Flask(__name__)
app.register_blueprint(facebook_group_widget, url_prefix='/fbgroup')

if __name__ == '__main__':
    app.run(debug=True)
