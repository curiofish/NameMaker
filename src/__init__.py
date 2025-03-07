from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'  # 실제 운영 환경에서는 안전한 키로 변경해야 합니다

    from .routes import main
    app.register_blueprint(main)

    return app 