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

# Creating blueprint
bp_problems = Blueprint('problems', __name__)
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
    
    '''
    The following method is designed to get all problems list. The problems can be arranged by some
    search condition inputted by admin (the search categories are: level and topic).

    :param object self: A must present keyword argument
    :return: All problems list that have not been deleted yet and satisfy search condition
    '''
    @jwt_required
    @admin_required
    def get(self):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('level', location = 'args', required = False)
        parser.add_argument('topic', location = 'args', required = False)
        parser.add_argument('page', location = 'args', required = True, type = int)
        args = parser.parse_args()

        # Query all problems
        problems_list = Problems.query
        
        # Search by level
        if args['level'] != '' and args['level'] != None and args['level'] != 'Semua Level':
            problems_list = problems_list.filter_by(level = args['level'])
        if problems_list.first() is None:
            return [], 200

        # Prepare the data to be shown
        problems_list_to_show = []
        for problem in problems_list:
            # Searching all topics related to this problem
            related_problem_topic_instances = ProblemTopics.query.filter_by(problem_id = problem.id).all()
            related_topics = []
            for problem_topic_instance in related_problem_topic_instances:
                topic = Topics.query.filter_by(id = problem_topic_instance.topic_id).first()
                related_topics.append(topic.topic)
            
            # Foramtting topics list into a string
            related_topics = ", ".join(related_topics)
        
            # Format shown data
            problem = marshal(problem, Problems.response_fields)
            problem['topic'] = related_topics
            problems_list_to_show.append(problem)

        # Search by topic
        if args['topic'] != '' and args['topic'] != None and args['topic'] != 'Semua Topik':
            topic_inputted = Topics.query.filter_by(topic = args['topic']).first()
            
            # Check whether the topic exist or not
            if topic_inputted is None:
                return [], 200
            else:
                topic_id = topic_inputted.id

            # Get all problems ID that related to the topic inputted
            all_problem_topics_related = ProblemTopics.query.filter_by(topic_id = topic_id)
            related_problem_id_list = []
            for problem_topic in all_problem_topics_related:
                related_problem_id_list.append(problem_topic.problem_id)
            
            # Filter all problems which ID in related_problem_id_list
            problems_list_to_show = filter(lambda problem: problem['id'] in related_problem_id_list, problems_list_to_show)
            problems_list_to_show = list(problems_list_to_show)

        # ---------- Pagination ----------
        problem_per_page = 15
        number_of_problems_to_show = len(problems_list_to_show)
        min_order = (args['page'] - 1) * problem_per_page

        # Check the index
        if min_order > number_of_problems_to_show - 1:
            return {'message': 'Halaman yang kamu minta tidak tersedia'}, 404

        max_order = min(len(problems_list_to_show), args['page'] * problem_per_page)
        problems_list_to_show = problems_list_to_show[min_order: max_order]
        # ---------- End of Pagination ----------

        return problems_list_to_show, 200

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

# Endpoint in problem route
api.add_resource(ProblemsResource, '')