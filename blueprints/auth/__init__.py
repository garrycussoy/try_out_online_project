# Import from standard libraries
import json
import hashlib

# Import from related third party
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

# Creating blueprint
bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

'''
The following class is designed for admin login section.
'''
class LoginAdmin(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200

    '''
    The following method is designed for admin login section

    :param object self: A must present keyword argument
    :return: Give success message and generate token when success, and a failure message otherwise
    '''
    def post(self):
        # Hard coded username and password
        admin_username = 'garrycussoy'
        admin_password = 'Garryac1'
        admin_password = hashlib.md5(admin_password.encode()).hexdigest()

        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json', required = True)
        parser.add_argument('password', location = 'json', required = True)
        args = parser.parse_args()
        
        # Checking whether there is an empty field or not
        if (args['username'] == None or args['username'] == '') or (args['password'] == None or args['password'] == ''):
            return {'message': 'Tidak boleh ada kolom yang dikosongkan'}, 400

        # Checking whether the username and password match or not
        encrypted = hashlib.md5(args['password'].encode()).hexdigest()
        if args['username'] != admin_username or encrypted != admin_password:
            return {'message': 'Username atau password yang kamu masukkan salah'}, 401

        # Create the token
        token = create_access_token(identity = admin_username, user_claims = {'username': admin_username})
        return {'message': 'Login berhasil', 'token': token}, 200

# Endpoint in Auth
api.add_resource(LoginAdmin, '')