from flask import Blueprint, request, jsonify
from utils.auth import require_auth, require_role
from utils.database import execute_query

bp = Blueprint('users', __name__, url_prefix='/api/users')