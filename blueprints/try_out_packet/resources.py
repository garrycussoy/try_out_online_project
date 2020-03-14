# Import from standard libraries
import json
from datetime import datetime, timedelta, date

# Import from related third party
from blueprints import db, app, admin_required
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy import desc

# Import models
from blueprints.try_out_packet.model import TryOutPacket
from blueprints.try_out_problems.model import TryOutProblems

# Creating blueprint
bp_test = Blueprint('test', __name__)
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

    '''
    The following method is designed to get all tests list with some information about them. The tests shown
    can be filtered by test name.

    :param object self: A must present keyword argument
    :return: Return all available tests list with some information about them, that satisfy the filter
    contsraint inputted by admin
    '''
    @jwt_required
    @admin_required
    def get(self):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('name', location = 'args', required = False)
        args = parser.parse_args()

        # Query all tests available
        tests_available = TryOutPacket.query.filter_by(deleted_at = None).filter_by(is_show = True)

        # Search by name
        if args['name'] != '' and args['name'] is not None:
            tests_available = tests_available.filter(TryOutPacket.name.like("%" + args['name'] + "%"))

        # Prepare the data to be shown
        tests_to_show = []
        for test in tests_available:
            test = marshal(test, TryOutPacket.response_fields)
            tests_to_show.append(test)
        return tests_to_show, 200

    '''
    The following method is designed to post a new test.

    :param object self: A must present keyword argument
    :return: Gives failure message if the proccess failed, and return all information of the posted test
    otherwise
    '''
    @jwt_required
    @admin_required
    def post(self):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('name', location = 'json', required = True)
        parser.add_argument('description', location = 'json', required = True)
        parser.add_argument('is_show', location = 'json', required = True, type = bool)
        parser.add_argument('time_limit', location = 'json', required = True, type = int)
        parser.add_argument('mc_correct_scoring', location = 'json', required = True, type = int)
        parser.add_argument('mc_wrong_scoring', location = 'json', required = True, type = int)
        parser.add_argument('sa_correct_scoring', location = 'json', required = True, type = int)
        parser.add_argument('sa_wrong_scoring', location = 'json', required = True, type = int)
        parser.add_argument('problems', location = 'json', type = list)
        args = parser.parse_args()

        # Check for emptyness
        if (
            args['name'] == '' or args['name'] == None
            or args['description'] == '' or args['description'] == None
            or args['is_show'] == '' or args['is_show'] == None
            or args['time_limit'] == '' or args['time_limit'] == None
            or args['mc_correct_scoring'] == '' or args['mc_correct_scoring'] == None
            or args['sa_correct_scoring'] == '' or args['sa_correct_scoring'] == None
            or args['mc_wrong_scoring'] == '' or args['mc_wrong_scoring'] == None
            or args['sa_wrong_scoring'] == '' or args['sa_wrong_scoring'] == None
            or args['problems'] == '' or args['problems'] == []
        ):
            return {'message': 'Tidak boleh ada kolom yang dikosongkan'}, 400
        
        # Check for positivity
        if args['time_limit'] <= 0:
            return {'message': 'Batas waktu harus bernilai positif'}, 400

        # Prepare some variables needed
        sa_total_problem = 0
        mc_total_problem = 0

        # Counting total problems of each type
        for problem in args['problems']:
            if problem['type'] == 'Isian Singkat':
                sa_total_problem += 1
            elif problem['type'] == 'Pilihan Ganda':
                mc_total_problem += 1

        # Calculate maximum score
        mc_max_score = mc_total_problem * args['mc_correct_scoring']
        sa_max_score = sa_total_problem * args['sa_correct_scoring']
        max_score = mc_max_score + sa_max_score

        # Create new record in "TryOutPacket" table
        new_try_out_packet = TryOutPacket(
            name = args['name'],
            description = args['description'],
            is_show = args['is_show'],
            time_limit = args['time_limit'],
            maximum_score = max_score,
            mc_total_problem = mc_total_problem,
            sa_total_problem = sa_total_problem,
            mc_correct_scoring = args['mc_correct_scoring'],
            mc_wrong_scoring = args['mc_wrong_scoring'],
            sa_correct_scoring = args['sa_correct_scoring'],
            sa_wrong_scoring = args['sa_wrong_scoring']
        )
        db.session.add(new_try_out_packet)
        db.session.commit()

        # Looping through all problems inputted
        for problem in args['problems']:
            # Create new record in "TryOutProblems" table
            new_try_out_problem = TryOutProblems(new_try_out_packet.id, problem['id'])
            db.session.add(new_try_out_problem)
            db.session.commit()
        
        # Prepare the data to be shown
        new_try_out_packet = marshal(new_try_out_packet, TryOutPacket.response_fields)
        new_try_out_packet['problems'] = args['problems']
        return {'message': 'Sukses membuat paket tes baru', 'detail_test': new_try_out_packet}, 200

# Endpoint in test route
api.add_resource(TestResource, '')