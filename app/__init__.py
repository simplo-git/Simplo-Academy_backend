from flask import Flask
from app.src.routes.db_routes import db_bp
from app.src.routes.user_routes import user_bp
from app.src.routes.role_routes import role_bp
from app.src.routes.certificate_routes import certificate_bp
from app.src.routes.activity_template_routes import activity_template_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    CORS(app)

    # Register Blueprints
    app.register_blueprint(db_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(role_bp, url_prefix='/api')
    app.register_blueprint(certificate_bp, url_prefix='/api')
    app.register_blueprint(activity_template_bp, url_prefix='/api')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
