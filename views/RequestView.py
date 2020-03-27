import json, bcrypt, jsonify, traceback, datetime
from flask import request, send_from_directory
from flask_classy import FlaskView, route
from models.base import session, engine
from models.Models import User, Info, Ddrows, Request, Customer
from cerberus import Validator
from cerberus.errors import ValidationError
from libs.BuValidator import BuValidator
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from pprint import pprint
from common import jwt, csrf
import traceback
import chardet

@jwt.invalid_token_loader
def invalid_token_loader(message):
    """Request ийн token зөв эсэхийг шалгана

    Args:
        message: Token буруу бол өгөх алдааны мессеж
    Return:
        json data
    """
    print('cc')
    return json.dumps({'result':'error','msg':message})

@jwt.expired_token_loader
def expired_token_loader(message):
    return json.dumps({'result':"error",'msg':"Token expired"})

        
class RequestView(FlaskView):
    """Монгол Банкин дээрх зээлийн мэдээллийг авах
       хүсэлт үүсгэх, мэдээллийг татах үйл ажилагааг эхлүүлэх,
       дууссаныг бусад серверүүдэд мэдээллэх сигналаар хангана.
       Мөн татагдсан мэдээллийг гаргаж өгөх үйл ажиллагаануудыг хариуцана.
    """    
            
    @jwt_required
    def before_request(self,name,*args, **kwargs):
        """Бүх хүсэлтийг jwt token тай байх ёстойг мөн нэвтэрсэн хэрэгчийг тодорхойлж байна        
        """
        id = get_jwt_identity()

        self.auth = session.query(User).filter_by(uuid=id).first()

    def after_request(self, name, response):
        """Бүх response ийн Content-Type ийг json оор тодорхойлно.
        """
        response.content_type = 'application/json; charset=utf-8'
        return response

    @csrf.exempt
    @route('getpendingrequest',methods = ['POST'])
    @jwt_required
    def getpendingrequest(self):
        try:
            requestParams ={
                'fields': { 
                    'action': {
                        "type":"string",
                        "required":True
                        }                    
                },
                'message': {
                    'action': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "required":"Утга тодорхойгүй байна"}                   
                }
            }
            
            v = BuValidator(requestParams)            
            v.validate(request.json)

            q = session.query(Request)\
                .filter(Request.status==Request.STATUS_PENDING)\
                .filter(Request.action==request.json['action'])
            count = q.count()
            print('count:',count)
            req = None
            if(count>0):
                row = q.first()
                req = {
                    'id':row.id,
                    'request':json.loads(row.request)
                }
                row.status = Request.STATUS_PROCESSING
                

            return json.dumps({
                'result':'success',
                'count':count,                
                'req':req

            },ensure_ascii=False).encode('utf8')

        except Exception as e:            
            msg =  e.args if len(e.args)>0 else str(e)            
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')
    
    @csrf.exempt
    @route('setresponse',methods = ['POST'])
    @jwt_required
    def setresponse(self):
        try:
            requestParams ={
                'fields': {
                    "id": {
                        "type":"integer",
                        "required":True},
                    'action': {
                        "type":"string",
                        "required":True},
                    'response': {
                        "type":"string",
                        "required":True}
                },
                'message': {
                    'id': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "required":"Утга тодорхойгүй байна"},
                    'action': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "required":"Утга тодорхойгүй байна"},
                    'response': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "required":"Утга тодорхойгүй байна"}
                }
            }
            
            v = BuValidator(requestParams)            
            v.validate(request.json)
            ucount = session.query(Request)\
                        .filter(Request.id==request.json['id'])\
                        .filter(Request.status==Request.STATUS_PROCESSING)\
                        .update({
                            'status':Request.STATUS_FINISHED, #'response':request.json['response'],
                            'updated_at':datetime.datetime.now()
                        })
            
                
            if(ucount>0):
                if(request.json['action']=="searchbyname"):
                    res =json.loads(request.json['response'])
                    if('result' in res):
                        for x in res['result']:
                            c = session.query(Customer).filter_by(rnumber=x[3]).first()
                            if(c is None):
                                session.add(Customer(id=x[0],rnumber=x[3],lastname=x[1],firstname=x[2]))
                                session.flush()
            
            return json.dumps({
                'result':'success'
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            traceback.print_exc()
            msg =  e.args if len(e.args)>0 else str(e)            
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')

