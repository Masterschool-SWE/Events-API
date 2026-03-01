from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from models import db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.rsvps import rsvps_bp
import yaml
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)
    
    # Swagger UI configuration
    SWAGGER_URL = '/apidocs'
    API_URL = '/api/openapi.yaml'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Evently API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Serve OpenAPI spec file
    @app.route('/api/openapi.yaml')
    def serve_openapi():
        return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(rsvps_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': 'Evently API',
            'version': '1.0.0',
            'description': 'A Flask-based REST API for managing events and RSVPs with different access levels',
            'documentation': {
                'swagger_ui': '/apidocs',
                'openapi_spec': '/api/openapi.yaml'
            },
            'endpoints': {
                'health': '/api/health',
                'auth': {
                    'register': '/api/auth/register',
                    'login': '/api/auth/login'
                },
                'events': {
                    'list': '/api/events',
                    'get': '/api/events/{id}',
                    'create': '/api/events'
                },
                'rsvps': {
                    'rsvp': '/api/rsvps/event/{event_id}',
                    'get_rsvps': '/api/rsvps/event/{event_id}'
                }
            }
        }), 200
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)

