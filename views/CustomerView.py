from flask import request, render_template,redirect, send_from_directory
from flask_classy import FlaskView, route
from models.Models import User, Info, Ddrows, Request, Customer
from models.base import session, engine
from sqlalchemy import or_
from sqlalchemy.orm import load_only
import libs.Bufunctions as bu
import json
from os import path
from cerberus import Validator
from cerberus.errors import ValidationError
from libs.BuValidator import BuValidator
from pprint import pprint
from flask_wtf import csrf

class CustomerView(FlaskView):

    @route('',methods=['GET'])
    @route('index',methods=['GET'])    
    def index(self):
        
        data = {
            "token_csrf":csrf.generate_csrf()
        }
        return render_template("customer/index.html",data=data)


    @route('jsonlist',methods=['POST'])    
    def jsonlist(self):        

        q = session.query(Customer)
        recordsTotal = q.count()
        start = request.json['start'] if('start' in request.json) else 0
        perpage = request.json['length'] if ('length' in request.json) else 10

        if('search' in request.json and request.json['search']['value'].strip()!=''):
            searchvalue=request.json['search']['value'].strip()            
            
            q = q.filter(or_(Customer.rnumber.like("%{}%".format(searchvalue)),Customer.firstname.like("{}%".format(searchvalue))))

        recordsFiltered = q.count()
        data = q.offset(start).limit(perpage).all()
        
        if('draw' in request.json): draw = request.json['draw']+1
        else: draw=1            

        return json.dumps({
                'result':'success',
                "draw": draw,
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsFiltered,
                "pageLength":10,
                'data': [x.listObj() for x in data]
            },ensure_ascii=False)


    @route('search',methods = ['GET'])
    def search(self):
        return render_template('customer/citizensearch.html')


    @route('crequest',methods=['POST'])
    def crequest(self):
        
        try:
            requestParams ={
                'fields': { 
                    'name': {
                        "type":"string",
                        "minlength":2,
                        "required":True
                        }                    
                },
                'message': {
                    'name': {
                        "type":"Нэр буруу байна",
                        "minlength":"Нэр буруу байна",
                        "required":"Нэр тодорхойгүй байна"},                    
                }
            }
            
            v = BuValidator(requestParams)
            dd = request.form.to_dict()
            del(dd['csrf_token'])            
            v.validate(dd)
            
            req = json.dumps({
                "inputVal":request.form['name'],
                "expression":"c.customername",
                "id":"01",
                "isCitizen":"true"
            },ensure_ascii=False).encode('utf8')
            
            cc = session.query(Request)\
                .filter(Request.action=="searchbyname")\
                .filter(Request.request==req)\
                .filter(Request.status.in_((0,1)))\
                .count()            
            if(cc==0):
                session.add(Request(action="searchbyname",request=req))
                session.flush()
            return redirect("/customer/index")

        except Exception as e:
            msg =  e.args if len(e.args)>0 else str(e)
            print(msg)
            return redirect("/customer/search")
    

    

