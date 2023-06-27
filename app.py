from flask import Flask # from f:소문자, import F:대문자
from flask_restful import Api # A 구분
from config import Config 
from flask_jwt_extended import JWTManager

from resources.user import UserRegisterResource



app= Flask(__name__) # 여기도 F:대문자
print('app 변수 생성') # 디버깅용

# 환경변수 세팅
app.config.from_object(Config) # config.py class config 상속(?)받음

        # JWT 매니저 초기화
# Flask-JWT-Extended 확장에 대한
# JWT 설정 및 콜백 기능을 보유하는 데 사용되는 개체..?
jwt= JWTManager(app)
print('jwt 매니저 초기화') # 디버깅용

api = Api(app) # api 변수에 Flask를 넣음

api.add_resource(UserRegisterResource, '/user/register')





if __name__== '__main__':
    app.run()
    