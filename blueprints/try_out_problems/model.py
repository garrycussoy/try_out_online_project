# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

# Import other models
from blueprints.try_out_packet.model import TryOutPacket
from blueprints.problems.model import Problems

'''
The following class is used to make the model of "TryOutProblems" table.
'''
class TryOutProblems(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'try_out_problems'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    try_out_id = db.Column(db.Integer, db.ForeignKey('try_out_packet.id'), nullable = False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "TryOutProblems" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'try_out_id': fields.Integer,
        'problem_id': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "TryOutProblems" class
    def __init__(self, try_out_id, problem_id):
        self.try_out_id = try_out_id
        self.problem_id = problem_id

    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Try Out ID " + str(self.try_out_id) + " (Problem ID: " + str(self.problem_id) + ")"