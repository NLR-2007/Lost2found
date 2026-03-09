from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from config import Config

def create_app():
    app = Flask(__name__, static_folder="frontend")
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Setup JWT
    jwt = JWTManager(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints (will be imported later)
    from api.auth import auth_bp
    from api.items import items_bp
    from api.admin import admin_bp
    from api.match import match_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(items_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(match_bp, url_prefix='/api')

    # Serve uploaded images
    @app.route('/uploads/<filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Serve static frontend files
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
