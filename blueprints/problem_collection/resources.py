# Import from standard libraries
import json
from datetime import datetime, timedelta, date

# Import from related third party
from blueprints import db, app
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy import desc

# Import models
from blueprints.problems.model import Problems
from blueprints.topics.model import Topics
from blueprints.problem_topics.model import ProblemTopics

# Creating blueprint
bp_problem_collection = Blueprint('problem_collection',__name__)
api = Api(bp_problem_collection)

'''
The following class is designed to provide every information needed to be shown on "Problem Collection" page.
'''
class ProblemCollectionPage(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200

# Endpoint in problem-collection route
api.add_resource(ProblemCollectionPage, '/')