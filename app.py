from flask import Flask, request, jsonify
from flask_migrate import Migrate

from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime

from config import Config
from models import db, bcrypt, User, SleepEntry

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


# HOME
@app.route("/")
def home():
    return {"message": "Sleep Tracker API Running"}

# SIGNUP
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}, 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password:
        return {"error": "username and password required"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 400

    user = User(username=username, email=email)
    user.password = password

    db.session.add(user)
    db.session.commit()

    return {"message": "User created"}, 201

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}, 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "username and password required"}, 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = create_access_token(identity=user.id)
        return {"token": token}, 200

    return {"error": "Invalid credentials"}, 401


# ME (CURRENT USER)
@app.route("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

# CREATE SLEEP ENTRY
@app.route("/sleep", methods=["POST"])
@jwt_required()
def create_sleep():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}, 400

    try:
        sleep = SleepEntry(
            sleep_time=datetime.fromisoformat(data.get("sleep_time")),
            wake_time=datetime.fromisoformat(data.get("wake_time")),
            quality=data.get("quality"),
            notes=data.get("notes"),
            user_id=user_id
        )
    except Exception:
        return {"error": "Invalid date format. Use ISO format"}, 400

    db.session.add(sleep)
    db.session.commit()

    return {"message": "Sleep entry created"}, 201

# GET SLEEP ENTRIES (PAGINATION)
@app.route("/sleep", methods=["GET"])
@jwt_required()
def get_sleep():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    data = SleepEntry.query.filter_by(user_id=user_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "sleep_entries": [
            {
                "id": s.id,
                "sleep_time": str(s.sleep_time),
                "wake_time": str(s.wake_time),
                "quality": s.quality,
                "notes": s.notes
            }
            for s in data.items
        ],
        "total_pages": data.pages,
        "current_page": page
    })

# UPDATE SLEEP ENTRY
@app.route("/sleep/<int:id>", methods=["PATCH"])
@jwt_required()
def update_sleep(id):
    user_id = get_jwt_identity()

    sleep = SleepEntry.query.filter_by(id=id, user_id=user_id).first()

    if not sleep:
        return {"error": "Not found"}, 404

    data = request.get_json()

    if "sleep_time" in data:
        sleep.sleep_time = datetime.fromisoformat(data["sleep_time"])

    if "wake_time" in data:
        sleep.wake_time = datetime.fromisoformat(data["wake_time"])

    if "quality" in data:
        sleep.quality = data["quality"]

    if "notes" in data:
        sleep.notes = data["notes"]

    db.session.commit()

    return {"message": "Updated successfully"}

# DELETE SLEEP ENTRY
@app.route("/sleep/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_sleep(id):
    user_id = get_jwt_identity()

    sleep = SleepEntry.query.filter_by(id=id, user_id=user_id).first()

    if not sleep:
        return {"error": "Not found"}, 404

    db.session.delete(sleep)
    db.session.commit()

    return {"message": "Deleted successfully"}


if __name__ == "__main__":
    app.run(port=5555, debug=True)