# Import from standard libraries
import json
import os
from datetime import timedelta
from functools import wraps

# Import from related third party
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims, get_raw_jwt
from flask_cors import CORS

# Import modules related to routing
from blueprints.auth.__init__ import bp_auth

# A step to prevent CORS
app = Flask(__name__)
CORS(app)

# Set the following to true, if you want to auto-reload when there is a change, or false otherwise
app.config['APP_DEBUG'] = True

# JWT setup
app.config['JWT_SECRET_KEY'] = 'c2n!$st0pDo1ngt#!s$tuff'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# Database setup
db_user=os.getenv('DB_USER')
db_pass=os.getenv('DB_PASS')
db_url=os.getenv('DB_URL')
db_selected=os.getenv('DB_SELECTED')

# Setup environment for testing (include changing schema in database)
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Garryac1@0.0.0.0:3306/try_out_online_project'
except Exception as e:
    raise e

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Register routes
app.register_blueprint(bp_auth, url_prefix='')

# Handle response from a request
@app.after_request
def after_request(response):
    try:
        request_data = response.get_json()
    except Exception as e:
        request_data = response.args.to_dict()
    
    log_data = json.dumps({
        'status_code': response.status_code,
        'method': request.method,
        'code': response.status,
        'uri': request.full_path,
        'requedatetimest': request_data,
        'response': json.loads(response.data.decode('utf-8'))
    })
    log = app.logger.info("REQUEST_LOG\t%s", log_data) if response.status_code == 200 else app.logger.warning("REQUEST_LOG\t%s", log_data)
    return response