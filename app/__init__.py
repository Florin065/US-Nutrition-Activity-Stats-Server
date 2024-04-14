"""Initialize Flask app."""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

# webserver.task_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

log = logging.getLogger('florin')
log.setLevel(logging.INFO)
log_handler = RotatingFileHandler("webserver.log", maxBytes=10240, backupCount=10)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)

webserver.log = log

webserver.log.info("Webserver started")

from app import routes
