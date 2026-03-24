from flask import Blueprint, request, jsonify
from utils.database import execute_query

bp = Blueprint('auth', __name__, url_prefix='/api/auth')