from flask import Flask
from datetime import timedelta

from db_connector import database

db = database()

#initialise flask app
app = Flask(__name__)
app.secret_key = "toka fitness" #session management
# our login session timeline
app.permanent_session_lifetime = timedelta(minutes=10)
import  routes

if __name__ == "__main__":
    app.run(debug=True)#run flaks in debug mode