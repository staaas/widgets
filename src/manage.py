from flask import Flask
from flaskext.babel import Babel
from flaskext.script import Manager

from fbgroup import facebook_group_widget
from fbgroup.management.update import UpdateCommand

app = Flask(__name__)
app.register_blueprint(facebook_group_widget, url_prefix='/fbgroup')

app.config.from_pyfile('settings.cfg')
app.config.from_envvar('WIDGETS_SETTINGS')

# i18n
babel = Babel(app)

# command-line management
manager = Manager(app)
manager.add_command('update', UpdateCommand())

if __name__ == "__main__":
    manager.run()

