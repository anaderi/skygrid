import json
import datetime

from flask import request, jsonify

from .main import app
from ..generic.models import Worker, Job, User


@app.route('/')
def index():
    return "Hello, world!"
