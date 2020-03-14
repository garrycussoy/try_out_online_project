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
from blueprints.problems.model import Problems, Solutions
from blueprints.topics.model import Topics
from blueprints.problem_topics.model import ProblemTopics
from blueprints.try_out_problems.model import TryOutProblems

# Creating blueprint
bp_problems = Blueprint('problems', __name__)
api = Api(bp_problems)

'''
The following class is designed for posting a new problem.
'''
class ProblemsResource(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200
    
    '''
    The following method is designed to post new problem.

    :param object self: A must present keyword argument
    :return: A failure message (with the reason why the proccess is failed) when the proccess failed,
    or return every data related to the posted problem and success message if the proccess success
    '''
    @jwt_required
    @admin_required
    def post(self):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('level', location = 'json', required = True)
        parser.add_argument('topics', location = 'json', required = True, type = list)
        parser.add_argument('content', location = 'json', required = True)
        parser.add_argument('problem_type', location = 'json', required = True)
        parser.add_argument('answer', location = 'json', required = True)
        parser.add_argument('first_option', location = 'json', required = False)
        parser.add_argument('second_option', location = 'json', required = False)
        parser.add_argument('third_option', location = 'json', required = False)
        parser.add_argument('fourth_option', location = 'json', required = False)
        parser.add_argument('explanation', location = 'json', required = False)
        args = parser.parse_args()

        # Check whether tehre is an empty field or not
        if (
            args['level'] == '' or args['level'] == None
            or args['topics'] == []
            or args['content'] == '' or args['content'] == None
            or args['problem_type'] == '' or args['problem_type'] == None
            or args['answer'] == '' or args['answer'] == None
        ):
            return {'message': 'Semua kolom selain kolom opsi dan kolom solusi lengkap wajib diisi'}, 400
        
        # Handle special case when user choose multiple choice type but doesn't specify at least one option
        if args['problem_type'] == 'Pilihan Ganda' and (args['first_option'] == '' or args['first_option'] == None):
            return {'message': 'Untuk tipe soal pilihan ganda, kamu harus menyediakan setidaknya satu opsi lain'}, 400

        # ---------- Create records for associate table in the database ----------
        # ----- Create record for "Problems" table -----
        new_problem = Problems(
            level = args['level'],
            content = args['content'],
            problem_type = args['problem_type'],
            answer = args['answer'],
            first_option = args['first_option'],
            second_option = args['second_option'],
            third_option = args['third_option'],
            fourth_option = args['fourth_option']
        )
        db.session.add(new_problem)
        db.session.commit()

        # ----- Create record for "Topics" table if there is new topic inputted and also create record
        # for "ProblemTopics" table -----
        for topic in args['topics']:
            # Checking whether the topic has already exist or not
            exist_topics = Topics.query.filter_by(topic = topic).all()
            if len(exist_topics) == 0:
                # Create new record for "Topics" table and get its ID
                new_topic = Topics(topic)
                db.session.add(new_topic)
                db.session.commit()
                topic_id = new_topic.id
            else:
                # Get the exist topic ID
                topic_id = exist_topics[0].id
            
            # Create new record for "ProblemTopics" table
            new_problem_topic = ProblemTopics(new_problem.id, topic_id)
            db.session.add(new_problem_topic)
            db.session.commit()
        
        # ----- Create record for "Solutions" table -----
        new_solution = Solutions(new_problem.id, args['explanation'])
        db.session.add(new_solution)
        db.session.commit()

        # Return success message and the new posted data
        new_problem = marshal(new_problem, Problems.response_fields)
        new_problem['topics'] = args['topics']
        new_problem['solution'] = args['explanation']
        return {'message': 'Sukses menambahkan soal baru', 'new_problem': new_problem}, 200

'''
The following class is designed for all CRUD functionality for given problem ID
'''
class ProblemsResourceById(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :param integer problem_id: Problem ID specified in the URI
    :return: Status OK
    '''
    def options(self, problem_id = None):
        return {'status': 'ok'}, 200
    
    '''
    The following method is designed to get all information about a problem for a given problem ID

    :param object self: A must present keyword argument
    :param integer problem_id: Problem ID given by admin, when admin click on a problem to look at the
    problem detail
    :return: All information of that problem, if the problem exist, and give "not found" message otherwise
    '''
    @jwt_required
    @admin_required
    def get(self, problem_id):
        # Get related problem
        related_problem = Problems.query.filter_by(id = problem_id).filter_by(deleted_at = None).first()
        if related_problem is None:
            return {'message': 'Soal yang kamu cari tidak ditemukan'}, 404
        
        # Searching for topics
        topics = []
        problem_topics_list = ProblemTopics.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None)
        for problem_topic in problem_topics_list:
            related_topic = Topics.query.filter_by(id = problem_topic.topic_id).first()
            topics.append(related_topic.topic)
        
        # Formatting topics list into a string
        topics = ", ".join(topics)

        # Searching for related solution
        related_solution = Solutions.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None).first()
        explanation = related_solution.explanation

        # Prepare the data to be shown
        related_problem = marshal(related_problem, Problems.response_fields)
        related_problem['topic'] = topics
        related_problem['solution'] = explanation
        return related_problem, 200

    '''
    The following method is designed to edit a problem for a given ID problem.

    :param object self: A must present keyword argument
    :param integer problem_id: Problem ID given by admin, when admin click on a problem to edit it
    :return: All information of the edited problem, if edit proccess success, but give a failed message if
    the proccess failed
    '''
    @jwt_required
    @admin_required
    def put(self, problem_id):
        # Searching for related problem
        related_problem = Problems.query.filter_by(id = problem_id).filter_by(deleted_at = None).first()
        if related_problem is None:
            return {'message': 'Soal yang kamu cari tidak ditemukan'}, 404
        
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('level', location = 'json', required = True)
        parser.add_argument('topics', location = 'json', required = True, type = list)
        parser.add_argument('content', location = 'json', required = True)
        parser.add_argument('problem_type', location = 'json', required = True)
        parser.add_argument('answer', location = 'json', required = True)
        parser.add_argument('first_option', location = 'json', required = False)
        parser.add_argument('second_option', location = 'json', required = False)
        parser.add_argument('third_option', location = 'json', required = False)
        parser.add_argument('fourth_option', location = 'json', required = False)
        parser.add_argument('explanation', location = 'json', required = False)
        args = parser.parse_args()

        # Check whether tehre is an empty field or not
        if (
            args['level'] == '' or args['level'] == None
            or args['topics'] == []
            or args['content'] == '' or args['content'] == None
            or args['problem_type'] == '' or args['problem_type'] == None
            or args['answer'] == '' or args['answer'] == None
        ):
            return {'message': 'Semua kolom selain kolom opsi dan kolom solusi lengkap wajib diisi'}, 400
        
        # Handle special case when user choose multiple choice type but doesn't specify at least one option
        if args['problem_type'] == 'Pilihan Ganda' and (args['first_option'] == '' or args['first_option'] == None):
            return {'message': 'Untuk tipe soal pilihan ganda, kamu harus menyediakan setidaknya satu opsi lain'}, 400
        
        # ---------- Update records for associate table in the database ----------
        # ----- Update record for "Problems" table -----
        related_problem.level = args['level']
        related_problem.content = args['content']
        related_problem.problem_type = args['problem_type']
        related_problem.answer = args['answer']
        related_problem.first_option = args['first_option']
        related_problem.second_option = args['second_option']
        related_problem.third_option = args['third_option']
        related_problem.fourth_option = args['fourth_option']
        related_problem.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        
        # ----- Update record for "Solutions" table -----
        related_solution = Solutions.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None).first()
        related_solution.explanation = args['explanation']
        related_solution.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        # ----- Update record for "ProblemSolutions" table and create new record for "Topics" table if there
        # is new topic -----
        # Removing all old topics in the problem
        old_problem_topics = ProblemTopics.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None)
        for old_problem_topic in old_problem_topics:
            old_problem_topic.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            old_problem_topic.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()

        # Get all topics available
        topics_available = []
        all_topics = Topics.query
        for topic in all_topics:
            topics_available.append(topic.topic)

        # Looping through all inputted topics
        for topic in args['topics']:
            if topic not in topics_available:
                # Create new record in "Topics"
                new_topic = Topics(topic)
                db.session.add(new_topic)
                db.session.commit()
                topic_id = new_topic.id
            else:
                # Searching for topic ID
                related_topic = Topics.query.filter_by(topic = topic).first()
                topic_id = related_topic.id
            
            # Create new record in "ProblemTopics" table
            new_problem_topic = ProblemTopics(problem_id, topic_id)
            db.session.add(new_problem_topic)
            db.session.commit()

        # Return success message and the new posted data
        related_problem = marshal(related_problem, Problems.response_fields)
        related_problem['topics'] = args['topics']
        related_problem['solution'] = args['explanation']
        return {'message': 'Sukses mengubah soal', 'updated_problem': related_problem}, 200
    
    '''
    The following method is designed to delete a problem (soft deleted only)

    :param object self: A must present keyword argument
    :param integer problem_id: Problem ID given by admin, when admin click on a problem to delete it
    :return: All information of the deleted problem, if edit proccess success, but give a failed message if
    the proccess failed
    '''
    @jwt_required
    @admin_required
    def delete(self, problem_id):
        # Searching for related problem
        related_problem = Problems.query.filter_by(id = problem_id).filter_by(deleted_at = None).first()
        if related_problem is None:
            return {'message': 'Soal yang kamu cari tidak ditemukan'}, 404
        
        # Check whether the problem included in any test or not
        related_to_problems = TryOutProblems.query.filter_by(deleted_at = None).filter_by(problem_id = problem_id).first()
        if related_to_problems is not None:
            return {'message': 'Kamu tidak bisa menghapus soal ini karena soal ini digunakan untuk tes'}, 400
        
        # Update record in "Problems" table
        related_problem.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        related_problem.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        db.session.commit()

        # Update record in "Solutions" table
        related_solution = Solutions.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None).first()
        related_solution.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        related_solution.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")

        # Update record in "ProblemTopics" table and store all related topics to be shown
        related_topics = []
        related_problem_topics = ProblemTopics.query.filter_by(problem_id = problem_id).filter_by(deleted_at = None)
        for related_problem_topic in related_problem_topics:
            related_problem_topic.updated_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            related_problem_topic.deleted_at = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            related_topic = Topics.query.filter_by(id = related_problem_topic.topic_id).first()
            related_topics.append(related_topic.topic)
        
        # Format the list into a string
        related_topics = ", ".join(related_topics)

        # ----- Show the result -----
        related_problem = marshal(related_problem, Problems.response_fields)
        related_problem['topic'] = related_topics
        related_problem['solution'] = related_solution.explanation
        return {'message': 'Sukses menghapus soal', 'deleted_problem': related_problem}, 200

# Endpoint in problem route
api.add_resource(ProblemsResource, '')
api.add_resource(ProblemsResourceById, '/<problem_id>')