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
from blueprints.problems.model import Problems, Solutions

# Creating blueprint
bp_problems = Blueprint('problems',__name__)
api = Api(bp_problems)

'''
The following class is designed for getting all problems list and post a new problem.
'''
class ProblemsResource(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200

# Endpoint in problem route
api.add_resource(ProblemsResource, '/')