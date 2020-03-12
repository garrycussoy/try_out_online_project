# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

'''
The following class is used to make the model of "TryOutPacket" table.
'''
class TryOutPacket(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'try_out_packet'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(255), nullable = False, default = '')
    description = db.Column(db.Text, nullable = False, default = '')
    is_show = db.Column(db.Boolean, default = True)
    time_limit = db.Column(db.Integer, nullable = False, default = 0)
    maximum_score = db.Column(db.Integer, nullable = False, default = 0)
    mc_total_problem = db.Column(db.Integer, nullable = False, default = 0)
    sa_total_problem = db.Column(db.Integer, nullable = False, default = 0)
    mc_correct_scoring = db.Column(db.Integer, nullable = False, default = 0)
    mc_wrong_scoring = db.Column(db.Integer, nullable = False, default = 0)
    sa_correct_scoring = db.Column(db.Integer, nullable = False, default = 0)
    sa_wrong_scoring = db.Column(db.Integer, nullable = False, default = 0)
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "TryOutPacket" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'description': fields.String,
        'is_show': fields.Boolean,
        'time_limit': fields.Integer,
        'maximum_score': fields.Integer,
        'mc_total_problem': fields.Integer,
        'sa_total_problem': fields.Integer,
        'mc_correct_scoring': fields.Integer,
        'mc_wrong_scoring': fields.Integer,
        'sa_correct_scoring': fields.Integer,
        'sa_wrong_scoring': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "TryOutPacket" class
    def __init__(
        self, name, description, is_show, time_limit, maximum_score, mc_total_problem, sa_total_problem,
        mc_correct_scoring, mc_wrong_scoring, sa_correct_scoring, sa_wrong_scoring
    ):
        self.name = name
        self.description = description
        self.is_show = is_show
        self.time_limit = time_limit
        self.maximum_score = maximum_score
        self.mc_total_problem = mc_total_problem
        self.sa_total_problem = sa_total_problem
        self.mc_correct_scoring = mc_correct_scoring
        self.mc_wrong_scoring = mc_wrong_scoring
        self.sa_correct_scoring = sa_correct_scoring
        self.sa_wrong_scoring = sa_wrong_scoring

    # Reprsentative form to be shown in log
    def __repr__(self):
        return self.name