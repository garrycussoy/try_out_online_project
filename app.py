# Import from standard libraries
import json
import sys
import logging

# Import from related third party
from flask_restful import Api
from blueprints import app, manager
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.cache import SimpleCache

# Manage cache
cache = SimpleCache()

# To catch all 404 error type
api = Api(app, catch_all_404s=True)

# Main program
if __name__ == '__main__':
    try:
        if sys.argv[1]=='db':
            manager.run()
    except Exception as e:
        # Print message to console and handle storage logs
        logging.getLogger().setLevel('INFO')
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        log_handler = RotatingFileHandler('%s/%s' %(app.root_path, '../storage/log/app.log'), maxBytes=10000000, backupCount=10)
        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)
        app.run(debug=True, host='0.0.0.0', port=5000)