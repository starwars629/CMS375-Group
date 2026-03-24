from flask import Flask
from flask_cors import CORS
from routes import auth, books, fines, loans, reservations, users
from utils.database import init_db

app = Flask(__name__)
CORS(app)   # Allow frontend to connect

# Initialize database connection
init_db()

# Register route blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(books.bp)
app.register_blueprint(fines.bp)
app.register_blueprint(loans.bp)
app.register_blueprint(reservations.bp)
app.register_blueprint(users.bp)

if __name__ == '__main__':
    app.run(debug=True, port = 5000)