from flask import request, render_template,redirect, send_from_directory
from flask_classy import FlaskView, route
from models.Models import User, Info, Ddrows
from models.base import session, engine
import libs.Bufunctions as bu
import json
from os import path
from pprint import pprint
import time 


class HomeView(FlaskView):

    @route('',methods=['GET'])
    @route('index',methods=['GET'])
    def index(self):
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
        
        return render_template("home/index.html",data=data)
    
    @route('info/import/real',methods=['GET','POST'])
    def import_real(self):
        rlist = []
        if('rnumbers_file' in request.files):
            f = request.files['rnumbers_file']            
            rlist = [x.decode('utf-8') for x in f.stream.readlines()]
            
        elif('rnumbers' in request.form):
            rlist = request.form['rnumbers'].splitlines()
        print(rlist)
        if(len(rlist)>0):
            #data = request.form['rnumbers'].splitlines()
            rnumbers = bu.remove_duplicate(rlist)            
            
            for rnumber in rnumbers:                
                rnumber = rnumber.strip()
                
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
                    user_uuid='ab6ea344-ccd9-4e87-8e85-2d457a52d77e',
                    rnumber=rnumber,
                    params = json.dumps(params, ensure_ascii=False),
                    filename = filename,
                    mode= Info.MODE_REALTIME,
                    status=Info.STATUS_PENDING
                )
                session.add(info)

            session.flush()
            return redirect("/home/index")
        return render_template("info/import_real.html")

    @route('info/import/schedule',methods=['GET','POST'])
    def import_schedule(self):
        rlist = []
        if('rnumbers_file' in request.files):
            f = request.files['rnumbers_file']            
            rlist = [x.decode('utf-8') for x in f.stream.readlines()]
            
        elif('rnumbers' in request.form):
            rlist = request.form['rnumbers'].splitlines()

        if(len(rlist)>0):
            #data = request.form['rnumbers'].splitlines()
            rnumbers = bu.remove_duplicate(rlist)            
            
            for rnumber in rnumbers:                
                rnumber = rnumber.strip()

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
                    user_uuid='ab6ea344-ccd9-4e87-8e85-2d457a52d77e',
                    rnumber=rnumber,
                    params = json.dumps(params, ensure_ascii=False),
                    filename = filename,
                    mode= Info.MODE_SCHEDULE,
                    status=Info.STATUS_PENDING
                )
                session.add(info)

            session.flush()
            return redirect("/home/index")
        return render_template("info/import_schedule.html")
    
    @route('info/detail',methods=['GET','POST'])
    def info_detail(self):
        info = None
        ff=None
        
        if('rnumber' in request.form):
            row = session.query(Info).filter_by(rnumber=request.form['rnumber'],status=Info.STATUS_FINISHED).order_by(Info.created_at.desc()).first()
            if(row!=None and row.detail2!=None):
                ddrows = session.query(Ddrows).filter_by(registriindugaar=request.form['rnumber']).all()
                pp = json.loads(row.detail2)
                info = {
                    'profile':pp['profile']['res'],
                    'ddrows':ddrows
                }
                #pprint(row)
                folders = [
                    '/home/batbold/projects/terminals/MB-Terminal-Server1/infofiles/',
                    '/home/batbold/projects/terminals/MB-Terminal-Server2/infofiles/',
                    '/home/batbold/projects/terminals/MB-Terminal-Server3/infofiles/',
                    '/home/batbold/projects/terminals/MB-Terminal-Server4/infofiles/',
                    '/home/buguun/projects/XAC21/',
                    '/home/batbold/projects/terminals/MB-Terminal-Server5/infofiles/',
                    
                ]
                
                for folder in folders:
                    if(path.exists(folder+row.filename)):
                        ff = row.filename
                        break
                #print(ff)
        
        return render_template("info/detail.html",info=info,ff=ff)
    
    @route('info/getfile/<filename>',methods=['GET'])
    def info_getfile(self,filename):
        folders = [
            '/home/batbold/projects/terminals/MB-Terminal-Server1/infofiles/',
            '/home/batbold/projects/terminals/MB-Terminal-Server2/infofiles/',
            '/home/batbold/projects/terminals/MB-Terminal-Server3/infofiles/',
            '/home/batbold/projects/terminals/MB-Terminal-Server4/infofiles/',
            '/home/buguun/projects/XAC21/',
            '/home/batbold/projects/terminals/MB-Terminal-Server5/infofiles/',            
        ]

        ff=None
        for folder in folders:
            if(path.exists(folder+filename)):                
                ff = folder+filename
                return send_from_directory(folder,filename, as_attachment=True)

        return filename