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
from blueprints.problems.model import Problems
from blueprints.topics.model import Topics
from blueprints.problem_topics.model import ProblemTopics
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
        tests_available = TryOutPacket.query.filter_by(deleted_at = None)

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

'''
The following class is designed for CRUD functionality of test route for given Try Out ID.
'''
class TestResourceById(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :param integer try_out_id: Try out ID specifiied in the URI
    :return: Status OK
    '''
    def options(self, try_out_id = None):
        return {'status': 'ok'}, 200

    '''
    The following method is designed to get all information about a test based on the given try out ID.

    :param object self: A must present keyword argument
    :param integer try_out_id: Try out ID given by admin when admin clik on a test name in "Test Collection"
    page to see its detail
    :return: Return all information about that test and some information about the problems on it
    '''
    @jwt_required
    @admin_required
    def get(self, try_out_id = None):
        # Search for related try_out_packet
        related_test = TryOutPacket.query.filter_by(deleted_at = None).filter_by(id = try_out_id).first()
        if related_test is None:
            return {'message': 'Paket tes yang kamu cari tidak ditemukan'}, 404
        
        # Search for related problems
        problems = []
        to_problems = TryOutProblems.query.filter_by(deleted_at = None).filter_by(try_out_id = try_out_id)
        for to_problem in to_problems:
            # Searching for the problems
            problem = Problems.query.filter_by(deleted_at = None).filter_by(id = to_problem.problem_id).first()

            # Searching for topics
            problem_topics =  ProblemTopics.query.filter_by(deleted_at = None).filter_by(problem_id = problem.id)
            topics = []
            for problem_topic in problem_topics:
                topic = Topics.query.filter_by(id = problem_topic.topic_id).first()
                topics.append(topic.topic)
            topics = ", ".join(topics)

            # Formatting the problem
            problem = marshal(problem, Problems.response_fields)
            problem['topic'] = topics

            problems.append(problem)
        
        # Prepare the data to be shown
        related_test = marshal(related_test, TryOutPacket.response_fields)
        related_test['problems'] = problems
        return related_test, 200
    
    '''
    The following method is designed to edit name and description of a test, specified by try out ID.

    :param object self: A must present keyword argument
    :param integer try_out_id: Try out ID specified by admin when admin want to edit a test
    :return: Return all information about the editted test and some information about the problems on it. Also
    give a success or failure message
    '''
    @jwt_required
    @admin_required
    def put(self, try_out_id = None):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('name', location = 'json', required = True)
        parser.add_argument('description', location = 'json', required = True)
        parser.add_argument('is_show', location = 'json', required = False, type = bool)
        args = parser.parse_args()

        # Search for related try_out_packet
        related_test = TryOutPacket.query.filter_by(deleted_at = None).filter_by(id = try_out_id).first()
        if related_test is None:
            return {'message': 'Paket tes yang kamu cari tidak ditemukan'}, 404

        # Edit is_show variable only
        if args['is_show'] != '' and args['is_show'] is not None:
            related_test.is_show = args['is_show']
            related_test.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            db.session.commit()
            return {'message': 'Sukses mengubah variabel tampilkan', 'is_show': args['is_show']}, 200

        # Check for emptyness
        if args['name'] == '' or args['name'] is None or args['description'] == '' or args['description'] is None:
            return {'message': 'Tidak boleh ada kolom yang dikosongkan'}, 400
        
        # Update record in "TryOutPacket" table
        related_test.name = args['name']
        related_test.description = args['description']
        related_test.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        db.session.commit()

        # ---------- Prepare the data to be shown ----------
        # Search for related problems
        problems = []
        to_problems = TryOutProblems.query.filter_by(deleted_at = None).filter_by(try_out_id = try_out_id)
        for to_problem in to_problems:
            # Searching for the problems
            problem = Problems.query.filter_by(deleted_at = None).filter_by(id = to_problem.problem_id).first()

            # Searching for topics
            problem_topics =  ProblemTopics.query.filter_by(deleted_at = None).filter_by(problem_id = problem.id)
            topics = []
            for problem_topic in problem_topics:
                topic = Topics.query.filter_by(id = problem_topic.topic_id).first()
                topics.append(topic.topic)
            topics = ", ".join(topics)

            # Formatting the problem
            problem = marshal(problem, Problems.response_fields)
            problem['topic'] = topics

            problems.append(problem)
        
        # Serialize the test instance into JSON
        related_test = marshal(related_test, TryOutPacket.response_fields)
        related_test['problems'] = problems
        return {'message': 'Sukses mengubah nama dan deskripsi', 'test': related_test}, 200

    '''
    The following method is designed to delete a test, specified by Try Out ID.

    :param object self: A must present keyword argument
    :param integer try_out_id: Try out ID specified by admin when admin want to delete a test
    :return: Return all information about the deleted test and some information about the problems on it. Also
    give a success or failure message
    '''
    @jwt_required
    @admin_required
    def delete(self, try_out_id = None):
        # Search for related try_out_packet
        related_test = TryOutPacket.query.filter_by(deleted_at = None).filter_by(id = try_out_id).first()
        if related_test is None:
            return {'message': 'Paket tes yang kamu cari tidak ditemukan'}, 404
        
        # Update record in "TryOutPacket" table
        related_test.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        related_test.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        db.session.commit()

        # ---------- Prepare the data to be shown ----------
        # Search for related problems
        problems = []
        to_problems = TryOutProblems.query.filter_by(deleted_at = None).filter_by(try_out_id = try_out_id)
        for to_problem in to_problems:
            # Update record in "TryOutProblems" table
            to_problem.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            to_problem.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            db.session.commit()
            
            # Searching for the problems
            problem = Problems.query.filter_by(deleted_at = None).filter_by(id = to_problem.problem_id).first()

            # Searching for topics
            problem_topics =  ProblemTopics.query.filter_by(deleted_at = None).filter_by(problem_id = problem.id)
            topics = []
            for problem_topic in problem_topics:
                topic = Topics.query.filter_by(id = problem_topic.topic_id).first()
                topics.append(topic.topic)
            topics = ", ".join(topics)

            # Formatting the problem
            problem = marshal(problem, Problems.response_fields)
            problem['topic'] = topics

            problems.append(problem)
        
        # Serialize the test instance into JSON
        related_test = marshal(related_test, TryOutPacket.response_fields)
        related_test['problems'] = problems
        return {'message': 'Sukses menghapus paket tes', 'deleted_test': related_test}, 200

# Endpoint in test route
api.add_resource(TestResource, '')
api.add_resource(TestResourceById, '/<try_out_id>')