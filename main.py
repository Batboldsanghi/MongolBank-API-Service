from common import app
from views.AuthView import AuthView
from views.InfoView import InfoView
from views.HomeView import HomeView
from views.CustomerView import CustomerView
from views.RequestView import RequestView
import uuid, bcrypt, json
from pprint import pprint
#from flask_wtf.csrf import CSRFProtect


AuthView.register(app)
InfoView.register(app)
HomeView.register(app)
CustomerView.register(app)
RequestView.register(app)
#CSRFProtect(app)


@app.errorhandler(Exception)
def internal_error(error):        
    #pprint(dir(error))
    #pprint(error.code)    
    return json.dumps({
        "result":"error",
        "code":error.code,
        "msg":error.description
    })

@app.route('/',methods=['POST','GET'])
def home():
    return "hello world"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5016, debug=True)