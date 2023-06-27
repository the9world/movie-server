from flask_restful import Resource
from flask import request
from mysql.connector import Error
from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError # emaill 체크
from utils import check_password, hash_password # 비밀번호 암호화
from flask_jwt_extended import create_access_token, get_jwt, jwt_required # login 연장기능 섞여있음


class UserRegisterResource(Resource):
    # 회원가입
    def post(self):
        #  {"email": "aaa@naver.com", 
        #   "password": "1234",
        #   "name": "홍길동" 
        #   "gender": "male"}
        
        # 1. 클라이언트가 보낸 데이터를 받아준다.(body : JSON)
        data = request.get_json() # 유저에게 body:json으로 email, password, name, gender 입력 받음
        print(data) # 디버깅
        
        # 2. email 주소형식이 올바른지 확인한다.(email 체크)
        # $pip install email-validator
        try:
            validate_email(data['email']) # email 체크
                 
        except EmailNotValidError as e:
            return {'result':'fail', "error":str() }, 400 # 상태코드 응답
            
        # 3. 비밀번호 길이가 유효한지 체크한다.
        # 만약, 비번이 4자리 이상, 12자리 이하라고 한다면
        
        if len(data['password'])<4 or len(data['password'])>12 :
            return {'result': 'fail', 'error': '비밀번호 길이 오류'}, 400
        
        # 4. 비밀번호를 암호화 한다.
        # $pip install psycopg2-binary, $pip install passlib
        hashed_password= hash_password(data['password'])
        print(str(hashed_password)) # 디버깅 용(?)
        
        # 5. DB에 이미 있는지 확인한다.
        try :
            connection= get_connection()
            query= '''select * from user
                    where email = %s;'''
            record= (data['email'],)
            cursor= connection.cursor(dictionary=True)
            cursor.execute(query, record)
            
            result_list= cursor.fetchall()
            print(result_list) # 확인
            
            # 해당 email이 있다면 이미 회원이라고 출력
            if len(result_list)==1:
                return {'result':'fail', 'error':'이미 회원가입 한 사람'}, 400
            # 회원 정보가 없다면 가입을 위한 코드를 작성.
            query= '''insert into user
                                    (email, password, name, gender)
                                values
                                    (%s, %s, %s, %s);'''
            record= (data['email'], hashed_password,
                     data['name'], data['gender']) # password는 암호화 된 것으로 입력 한다.
            cursor= connection.cursor()
            cursor.execute(query, record)
            
            connection.commit() # DB 에 입력받은 데이터를 적용
            
            ### DB에 데이터를 insert 한 후에 insert된 행의 ID를 가져오는 코드!!
            # 회원가입 시 user_id가 노출되지 않게 인증토큰이 필요해, 클라이언트에게 보내줘야함
            user_id= cursor.lastrowid # id값이 증가(AI)된 것을 가져와라..?
            
            cursor.close()
            connection.close()
                        
        except Error as e :
            return {'result':'fail', 'error':str(e)}, 500 # DB Error
        
        # create_access_token(user_id, expires_delta=datetime.timedelta(days=10)) # 로그인 연장
        access_token= create_access_token(user_id)
        return {'result': 'success', 'access_token' :access_token}


### 로그인 관련 개발
class UserloginResource(Resource):
    def post(self):
    #{
    # "email": "aaa@naver.com", 
    # "password": "1234"
    #}
        # 1. 클라이언트로부터 데이터를 받아온다
        data= request.get_json()
        # 2. 이메일 주소로 DB에 Select 한다.
        