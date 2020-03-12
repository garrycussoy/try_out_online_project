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
from blueprints.try_out_packet.model import TryOutPacket
from blueprints.try_out_problems.model import TryOutProblems

# Creating blueprint
bp_test = Blueprint('test',__name__)
api = Api(bp_test)

'''
The following class is designed to get all try out list and post a new try out
'''
class TestResource(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200

# Endpoint in test route
api.add_resource(TestResource, '/')