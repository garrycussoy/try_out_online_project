# Import
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
import json , hashlib

# Creating blueprint
bp_auth = Blueprint('auth',__name__)
api = Api(bp_auth)

# CRUD options (CORS), post, get
class LoginApps(Resource):
    # Enable CORS
    def options(self,id=None):
        return{'status':'ok'} , 200
    
    def get(self, id=None):
        return{'status' : 'UNATUTHORIZED' , 'message' : 'Username atau Password Tidak Valid'}, 401

# Endpoint in Auth
api.add_resource(LoginApps, '/')