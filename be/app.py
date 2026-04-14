from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import db
from routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    app.register_blueprint(auth_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"message": "Flask backend is running"})

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=app.config["DEBUG"])