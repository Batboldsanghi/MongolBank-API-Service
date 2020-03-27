import json, bcrypt
from flask import request
from flask_classy import FlaskView, route
from models.base import session
from models.Models import User
from cerberus import Validator
from cerberus.errors import ValidationError
from libs.BuValidator import BuValidator
from flask_jwt_extended import (
    create_access_token
)
from pprint import pprint
from common import csrf


class AuthView(FlaskView):
    
    def after_request(self, name, response):        
        response.content_type = 'application/json; charset=utf-8'
        return response

    @route('index',methods=['POST'])
    def index(self):
        return json.dumps({"result":"success"})

    @csrf.exempt
    @route('token',methods=['POST'])    
    def token(self):
        try:
            
            loginParams = {
                "fields" : {
                    "email": {
                        "type": "string", 
                        "required": True, 
                        "regex": '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    },
                    "password": {"type": "string","required": True,"minlength":4}
                },
                "message" : {
                    "email":{
                        "type": "тэмдэгт оруулна уу",
                        "required": "email тодорхойгүй байна",
                        "regex": "имэйлээ зөв оруулна уу"
                    },
                    "password":{
                        "type": "Нууц үг үсэг тоо байна",
                        "required": "Нууц үг тодорхойгүй байна",
                        "minlength": "Нууц үг 4 олон тэмдэгттэй байна"
                    }
                }
            }
            

            v = BuValidator(loginParams)
            v.validate(request.json)
            email = request.json['email']
            password = request.json['password']
            user = session.query(User).filter_by(email=email).first()
            
            if(user==None):
                raise Exception('username,password is wrong')
            

            if(bcrypt.checkpw(password.encode("utf8"),user.password.encode("utf8"))==False):
                raise Exception('username,password is wrong')
            
            if(user.status!=User.STATUS_ACTIVE):
                raise Exception("user is not activation")
            #expires = datetime.timedelta(seconds=60)
            access_token = create_access_token(user.uuid) #,expires_delta=expires
            return json.dumps({
                'result':'success',
                'token':access_token,                
                'email':user.email,
                'role':user.role,
                'status':user.status
            })
            
        except Exception as e:
            
            msg =  e.args if len(e.args)>0 else str(e)
            return json.dumps({
                'result':'error',                
                'msg': msg
            },ensure_ascii=False).encode('utf8')

    @csrf.exempt
    @route('activation',methods=['POST'])
    def activation(self):
        try:
            activationParams = {
                "fields" : {
                    "email": {
                        "type": "string", 
                        "required": True, 
                        "regex": '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    },
                    "code":{"type":"string", "required": True}
                },
                "message" : {
                    "email":{
                        "type": "тэмдэгт оруулна уу",
                        "required": "email тодорхойгүй байна",
                        "regex": "имэйлээ зөв оруулна уу"
                    },
                    "code":{
                        "type": "Өгөгдлийн төрөл буруу байна",
                        "required": "Код тодорхойгүй байна"
                    }
                }
            }
            

            v = BuValidator(activationParams)
            v.validate(request.json)

            email = request.json['email']
            user = session.query(User).filter_by(email=email).first()
            if(user==None):
                raise Exception('email is wrong')

            if('code' in request.json):
                if(bcrypt.checkpw(request.json.get('code').encode("utf8"),user.activation.encode("utf8"))==False):
                    raise Exception('activation code is wrong')
                user.status=User.STATUS_ACTIVE
                session.flush()

            

            return json.dumps({
                'result':'success'
            })
        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')        

    @csrf.exempt
    @route('create',methods=['POST'])
    def create(self):
        try:
            createParams = {
                "fields" : {
                    "email": {
                        "type": "string", 
                        "required": True, 
                        "regex": '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    },
                    "password": {"type": "string","required": True,"minlength":4}
                },
                "message" : {
                    "email":{
                        "type": "тэмдэгт оруулна уу",
                        "required": "email тодорхойгүй байна",
                        "regex": "имэйлээ зөв оруулна уу"
                    },
                    "password":{
                        "type": "Нууц үг үсэг тоо байна",
                        "required": "Нууц үг тодорхойгүй байна",
                        "minlength": "Нууц үг 4 олон тэмдэгттэй байна"
                    }
                }
            }
            

            v = BuValidator(createParams)
            v.validate(request.json)
            code = '123456'
            password_hashed = bcrypt.hashpw(request.json['password'].encode("utf8"), bcrypt.gensalt())
            code_hashed = bcrypt.hashpw(code.encode("utf8"), bcrypt.gensalt())
            
            user = User(
                uuid=User.generateID(),
                email=request.json['email'],
                password = password_hashed,
                activation = code_hashed
            )            
            session.add(user)
            session.flush()
            return json.dumps({
                'result':'success' 
            })        
        except Exception as e:            
            msg =  e.args if len(e.args)>0 else str(e)
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')
