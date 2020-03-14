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
bp_problem_collection = Blueprint('problem_collection', __name__)
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
    
    '''
    The following method is designed to get all information needed to be shown in "Problem Collection" page.
    The problems in the problems list can be arranged by some search condition inputted by admin (the search 
    categories are: level and topic).

    :param object self: A must present keyword argument
    :return: All information needed to be shown in "Problem Collection" page
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

        # Query all non-deleted problems
        problems_list = Problems.query.filter_by(deleted_at = None)
        
        # Search by level
        if args['level'] != '' and args['level'] != None and args['level'] != 'Semua Level':
            problems_list = problems_list.filter_by(level = args['level'])
        if problems_list.first() is None:
            return [], 200

        # Prepare the data to be shown
        problems_list_to_show = []
        for problem in problems_list:
            # Searching all topics related to this problem
            related_problem_topic_instances = ProblemTopics.query.filter_by(problem_id = problem.id).filter_by(deleted_at = None).all()
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
            all_problem_topics_related = ProblemTopics.query.filter_by(topic_id = topic_id).filter_by(deleted_at = None)
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

        # ---------- Prepare the data to be shown ----------
        # Specify topic chosen
        topic_chosen = args['topic']
        if args['topic'] == '' or args['topic'] is None:
            topic_chosen = 'Semua Topik'
        
        # Specify level chosen
        level_chosen = args['level']
        if args['level'] == '' or args['level'] is None:
            level_chosen = 'Semua Level'

        # Get all available topics
        available_topics = []
        all_topics = Topics.query
        for topic in all_topics:
            available_topics.append(topic.topic)

        return {'available_topics': available_topics, 'topic_chosen': topic_chosen, 'level_chosen': level_chosen, 'problems_list': problems_list_to_show}, 200
        
# Endpoint in problem-collection route
api.add_resource(ProblemCollectionPage, '')