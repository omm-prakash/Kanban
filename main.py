import os
from flask import Flask
from flask_restful import Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.models import Account, Role
from flask_login import LoginManager

app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      app.logger.info("Currently no production config is setup.")
      raise Exception("Currently no production config is setup.")
    else:
      app.logger.info("Staring Local Development.")
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)


    app.app_context().push()
    app.logger.info("App setup complete")

    # Setup Flask-Security
    user_datastore = SQLAlchemySessionUserDatastore(db.session, Account, Role)
    security = Security(app, user_datastore)
    
    return app

app = create_app()

api = Api(app)
app.app_context().push()

from application.api import *

api.add_resource(ListApi, '/api/list/<string:email>/<string:list_name>', '/api/list/<string:email>')
api.add_resource(CardApi, '/api/card/<int:list_id>/<string:card_name>', '/api/card/<int:list_id>')
api.add_resource(SummaryApi, '/api/<string:email>/summary')

# Import all the controllers so they are loaded
from application.controllers import *


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(403)
def not_authorized(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403


if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=8080)
