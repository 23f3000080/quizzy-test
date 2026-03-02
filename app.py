from flask import Flask
from dotenv import load_dotenv
import os
from models import db

#app initialize
app = Flask(__name__)

#load environment variable
load_dotenv()

#app configure
# supabase configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

# initialize db with app
db.init_app(app)

from routes import main
app.register_blueprint(main)

from crud_routes import crud
app.register_blueprint(crud)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)