# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

'''
    The following class is used to make the model of "Topics" table
'''
class Topics(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    topic = db.Column(db.String(255), nullable = False, default = '')
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "Topics" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'topic': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "Topics" class
    def __init__(self, topic):
        self.topic = topic

    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Topic: " + self.topic