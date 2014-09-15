import json
import datetime

from flask import request, jsonify

from .main import app


@app.route('/')
def index():
    return "Hello, world!"
