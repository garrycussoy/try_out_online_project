# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

'''
The following class is used to make the model of "Problems" table.
'''
class Problems(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    level = db.Column(db.String(255), nullable = False, default = '')
    content = db.Column(db.Text, nullable = False, default = '')
    problem_type = db.Column(db.String(255), nullable = False, default = '')
    answer = db.Column(db.Text, nullable = False, default = '')
    first_option = db.Column(db.Text, default = '')
    second_option = db.Column(db.Text, default = '')
    third_option = db.Column(db.Text, default = '')
    fourth_option = db.Column(db.Text, default = '')
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "Problems" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'level': fields.String,
        'content': fields.String,
        'problem_type': fields.String,
        'answer': fields.String,
        'first_option': fields.String,
        'second_option': fields.String,
        'third_option': fields.String,
        'fourth_option': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "Problems" class
    def __init__(
        self, level, content, problem_type, answer, first_option, second_option, third_option, fourth_option
    ):
        self.level = level
        self.content = content
        self.problem_type = problem_type
        self.answer = answer
        self.first_option = first_option
        self.second_option = second_option
        self.third_option = third_option
        self.fourth_option = fourth_option

    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Problems ID " + str(self.id) + " (" + self.level + ")"

'''
The following class is used to make the model of "Solutions" table.
'''
class Solutions(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable = False)
    explanation = db.Column(db.Text, default = '')
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    deleted_at = db.Column(db.DateTime, nullable = True)

    # The following dictionary is used to serialize "Solutions" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'problem_id': fields.Integer,
        'explanation': fields.String,
        'created_at': fields.DateTime,
        'updated_at': fields.DateTime,
        'deleted_at': fields.DateTime
    }

    # Required fields when create new instances of "Solutions" class
    def __init__(self, problem_id, explanation):
        self.problem_id = problem_id
        self.explanation = explanation

    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Solution ID " + str(self.id) + " for Problem ID " + str(self.problem_id)