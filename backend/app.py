import logging
import os

from backend.config import Config
from backend.extensions import db, jwt, mail, migrate
from backend.routes import all_routes
from flask import Flask, send_file, send_from_directory
from flask_cors import CORS


# Docker container path
REACT_BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend/build')
# Local development path
# REACT_BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/build')

def create_app(testing=False):
    app = Flask(
        __name__,
        static_folder=os.path.join(REACT_BUILD_DIR, 'static'),
        static_url_path='/static'
    )
    app.config.from_object(Config)
    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False

    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    app.logger.setLevel(logging.INFO)

    # cors
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Register all blueprints from routes
    for bp in all_routes:
        app.register_blueprint(bp)

    # Serve images from build/img
    @app.route('/img/<path:filename>')
    def serve_img(filename):
        img_dir = os.path.join(REACT_BUILD_DIR, 'img')
        return send_from_directory(img_dir, filename)

    # favicon support
    @app.route('/favicon.png')
    def favicon():
        return send_from_directory(
            REACT_BUILD_DIR,
            'favicon.png',
            mimetype='image/vnd.microsoft.icon'
        )

    # Catch-all route for React SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path.startswith('api/'):
            return 'Not Found', 404
        return send_file(os.path.join(REACT_BUILD_DIR, 'index.html'))

    return app

# For development/production servers that expect `app`
app = create_app()
