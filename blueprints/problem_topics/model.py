# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

# Import other models
from blueprints.problems.model import Problems
from blueprints.topics.model import Topics

'''
The following class is used to make the model of "ProblemTopics" table.
'''
class ProblemTopics(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'problem_topics'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable = False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "ProblemTopics" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'problem_id': fields.Integer,
        'topic_id': fields.Integer,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "ProblemTopics" class
    def __init__(self, problem_id, topic_id):
        self.problem_id = problem_id
        self.topic_id = topic_id

    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Problem ID " + str(self.problem_id) + " (Topic ID: " + str(self.topic_id) + ")"