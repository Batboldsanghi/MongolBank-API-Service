import json, bcrypt, jsonify, traceback
from flask import request, send_from_directory
from flask_classy import FlaskView, route
from models.base import session, engine
from models.Models import User, Info, Ddrows
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

def make_me_unicode(s):
    if isinstance(s, str):
        return s.decode('utf-8')
    elif isinstance(s, unicode):
        return s
    else:
        return None
        
class InfoView(FlaskView):
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


    @route('index',methods=['POST'])
    @csrf.exempt
    def index(self):
        try:
            m1={
                'pending':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.STATUS_PENDING).count(),
                'error':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.STATUS_ERROR).count(),
                'finished':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.STATUS_FINISHED).count(),
                'c1pending':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.C1_STATUS_PENDING).count(),
                'c1error':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.C1_STATUS_ERROR).count(),
                'c1finished':session.query(Info).filter_by(mode=Info.MODE_REALTIME,status=Info.C1_STATUS_FINISHED).count()
            }
            m2 = {
                'pending':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.STATUS_PENDING).count(),
                'error':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.STATUS_ERROR).count(),
                'finished':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.STATUS_FINISHED).count(),
                'c1pending':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.C1_STATUS_PENDING).count(),
                'c1error':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.C1_STATUS_ERROR).count(),
                'c1finished':session.query(Info).filter_by(mode=Info.MODE_SCHEDULE,status=Info.C1_STATUS_FINISHED).count()
            }        
            data=[m1,m2]
            return json.dumps({
                'result':'success',
                'data':data
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            traceback.print_exc()
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')
            
    @route('create',methods=['POST'])
    @csrf.exempt
    def create(self):
        """Хүсэлт үүсгэх
        """
        try:
            requestParams ={
                'fields': { 
                    'rnumber': {
                        "type":"string", 
                        "registernumber": True,
                        "required":True
                        },
                    'mode': {
                        "type":"integer", 
                        "allowed": [0,1],
                        "required":True
                    }
                },
                'message': {
                    'rnumber': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "registernumber":"Регистрийн дугаар буруу байна",
                        "required":"Регистрийн дугаар тодорхойгүй байна"},
                    'mode': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "allowed":"Буруу утгатай байна",
                        "required":"Утга тодорхойгүй байна"}
                }
            }
            v = BuValidator(requestParams)
            v.validate(request.json)
            
            if(len(request.json['rnumber'])==10):
                #person
                params = {
                    'id':'01',
                    'expression':'c.registerno',
                    'inputVal':request.json['rnumber'],
                    'isCitizen': 'true'
                }
            else:
                #company
                params = {
                    'id':'03',
                    'expression':'c.registerno',
                    'inputVal':request.json['rnumber']
                }
            filename = Info.generateFilename()
            
            info = Info(
                user_uuid=self.auth.uuid,
                rnumber=request.json['rnumber'],
                params = json.dumps(params, ensure_ascii=False),
                filename = filename,
                mode= request.json['mode'],
                status=Info.STATUS_PENDING
            )
            
            session.add(info)
            session.flush()
            return json.dumps({
                'result':'success',
                'id':info.id
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            traceback.print_exc()
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')

    @route('creates',methods = ['POST'])
    @csrf.exempt
    def creates(self):
        try:
            requestParams ={
                'fields': { 
                    'rnumbers': {
                        "type":"list", 
                        "required":True
                        },
                    'mode': {
                        "type":"integer", 
                        "allowed": [0,1],
                        "required":True
                    }
                },
                'message': {
                    'rnumbers': {
                        "type":"өгөгдлийн төрөл буруу байна",                        
                        "required":"Регистрийн дугаар тодорхойгүй байна"},
                    'mode': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "allowed":"Буруу утгатай байна",
                        "required":"Утга тодорхойгүй байна"}
                }
            }
            v = BuValidator(requestParams)
            v.validate(request.json)
            for rnumber in request.json['rnumbers']:
                if(len(rnumber)==10):
                    #person
                    params = {
                        'id':'01',
                        'expression':'c.registerno',
                        'inputVal':rnumber,
                        'isCitizen': 'true'
                    } 
                elif(len(rnumber)==7):
                    #company
                    params = {
                        'id':'03',
                        'expression':'c.registerno',
                        'inputVal':rnumber
                    }
                else: continue

                filename = Info.generateFilename()
            
                info = Info(
                    user_uuid=self.auth.uuid,
                    rnumber=rnumber,
                    params = json.dumps(params, ensure_ascii=False),
                    filename = filename,
                    mode= request.json['mode'],
                    status=Info.STATUS_PENDING
                )
                session.add(info)

            session.flush()
            return json.dumps({
                'result':'success'
            },ensure_ascii=False).encode('utf8')
        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            traceback.print_exc()
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')

    @route('setDetail',methods=['POST'])
    @csrf.exempt
    def setDetail(self):
        """Монгол банкны мэдээлэлийг шинэчилж байна.
        """
        try:
            setDetailParams ={
                'fields': {
                    'id':{
                        'type':'integer',
                        'required': True
                    },
                    'rnumber': {
                        "type":"string",
                        "required": True,
                        "registernumber":True
                        },
                    'status': {
                        'type':'integer'
                    },
                    'detail': {
                        'type':'string',
                        'nullable':True
                    },
                    'detail2': {
                        'type':'string',
                        'nullable':True
                    }
                },
                'message': {
                    'id':{
                        'type':'Төрөл буруу байна',
                        'required':'id тодорхойгүй байна'
                    },
                    'rnumber': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "registernumber":"Регистрийн дугаар буруу байна",
                        "required":"Регистрийн дугаар тодорхойгүй байна"},
                    'status':{
                        'type':'Төрөл буруу байна'
                    },
                    'detail':{
                        'type':'Төрөл буруу байна'
                    },                    
                    'detail2':{
                        'type':'Төрөл буруу байна'
                    }
                }
            }

            v = BuValidator(setDetailParams)
            v.validate(request.json)
            
            row = session.query(Info).filter_by(id=request.json['id'],rnumber=request.json['rnumber']).first()
            if(row is None):
                raise Exception('бичлэг байхгүй байна')
            if('status' in request.json):
                row.status=request.json['status']
            if('detail' in request.json):
                row.detail = request.json['detail']
            if('detail2' in request.json):
                row.detail2 = request.json['detail2']
            session.flush()    

            return json.dumps({
                'result':'success',
                'row': row.to_dict()
            },ensure_ascii=False)
        except Exception as e:
            
            traceback.print_exc()
            msg =  e.args if len(e.args)>0 else str(e)
            
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')


    @route('get',methods=['POST'])
    @csrf.exempt
    def get(self):
        """Мэдээлэлийг авах
        """
        try:
            requestParams ={
                'fields': { 
                    'id': {
                        "type":"integer",                     
                        "required":True
                        },
                    'rnumber': {
                        "type":"string", 
                        "registernumber": True,
                        "required":True
                        },
                    'full': {
                        "type":"integer"
                    }
                },
                'message': {
                    'id': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "required":"Утга тодорхойгүй байна"},
                    'rnumber': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "registernumber":"Регистрийн дугаар буруу байна",
                        "required":"Регистрийн дугаар тодорхойгүй байна"},
                    'full': {
                        "type":"өгөгдлийн төрөл буруу байна"
                    }
                }
            }
            
            v = BuValidator(requestParams)            
            v.validate(request.json)
            
            q = session.query(Info).filter_by(id=request.json['id'],rnumber=request.json['rnumber'])
            
            if(q.count()!=1):
                raise Exception('бичлэг олдсонгүй')
            
            if('full' in request.json and request.json['full']==1):
                rows = session.query(Ddrows).filter_by(registriindugaar=request.json['rnumber']).all()
                qd=[]
                
                for row in rows:
                    tmprow = row.__dict__
                    tmprow['created_at']=tmprow['created_at'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['downloaded_date']=tmprow['downloaded_date'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['tologdokhognoo']=tmprow['tologdokhognoo'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['zeelolgosonognoo']=tmprow['zeelolgosonognoo'].strftime("%Y-%m-%d, %H:%M:%S")
                    pprint(tmprow)
                    if('_sa_instance_state' in tmprow):
                        tmprow.pop('_sa_instance_state')                        
                    qd.append(tmprow)                    
            else:
                qd=None
            
            return json.dumps({
                'result':'success',
                'info':q.first().to_dict(),
                'qd':qd
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            print(e)
            msg =  e.args if len(e.args)>0 else str(e)            
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')


    @route('detail',methods=['POST'])
    @csrf.exempt
    def detail(self):
        """Мэдээлэлийг авах
        """
        try:
            requestParams ={
                'fields': {                    
                    'rnumber': {
                        "type":"string", 
                        "registernumber": True,
                        "required":True
                        },
                    'full': {
                        "type":"integer"
                    }
                },
                'message': {
                    'rnumber': {
                        "type":"өгөгдлийн төрөл буруу байна",
                        "registernumber":"Регистрийн дугаар буруу байна",
                        "required":"Регистрийн дугаар тодорхойгүй байна"},
                    'full': {
                        "type":"өгөгдлийн төрөл буруу байна"
                    }
                }
            }
            
            v = BuValidator(requestParams)            
            v.validate(request.json)
            
            q = session.query(Info).filter_by(rnumber=request.json['rnumber'],status=Info.STATUS_FINISHED).order_by(Info.created_at.desc()).first()
            
            if(q is None):
                raise Exception('бичлэг олдсонгүй')
            info=q.to_dict()

            if('full' in request.json and request.json['full']==1):
                rows = session.query(Ddrows).filter_by(registriindugaar=request.json['rnumber']).all()
                qd=[]
                
                for row in rows:
                    tmprow = row.__dict__
                    tmprow['created_at']=tmprow['created_at'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['downloaded_date']=tmprow['downloaded_date'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['tologdokhognoo']=tmprow['tologdokhognoo'].strftime("%Y-%m-%d, %H:%M:%S")
                    tmprow['zeelolgosonognoo']=tmprow['zeelolgosonognoo'].strftime("%Y-%m-%d, %H:%M:%S")
                    
                    if('_sa_instance_state' in tmprow):
                        tmprow.pop('_sa_instance_state')                        
                    qd.append(tmprow)                    
            else:
                qd=None
            info['ddrows']=qd
            return json.dumps({
                'result':'success',
                'info':info
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            #print(e)
            msg =  e.args if len(e.args)>0 else str(e)            
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')


    @route('get_pendingdownload',methods=['POST'])
    @csrf.exempt
    def get_pendingdownload(self):
        """Хүлээгдэж байгаа мэдээлэл татах хүсэлтийг авах
        """
        try:            
            q = session.query(Info).filter(Info.status==Info.STATUS_PENDING)
            if('mode' in request.json):
                q.filter(Info.mode==request.json['mode'])            

            q.order_by(Info.created_at.asc())
            count = q.count()
            info = None
            if(count>0):
                row = q.first()
                info=row.to_dict()
                if('withprocess' in request.json and request.json['withprocess']==1):
                    row.status=Info.STATUS_PROCESSING
                session.flush()
            print(info)
            return json.dumps({
                'result':'success',
                'count':count,
                'info':info
            },ensure_ascii=False).encode('utf8')

        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            traceback.print_exc()
            return json.dumps({
                'result':'error',
                'msg': msg
            },ensure_ascii=False).encode('utf8')
    

    @route('delete',methods=['POST'])
    def delete(self):
        """
        """
        pass    