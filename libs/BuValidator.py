from cerberus import Validator
import cerberus.errors as ERRORS
from cerberus.errors import ValidationError, ErrorDefinition
from pprint import pprint

class CustomValidator(Validator):
    
    def _validate_registernumber(self, data, field, value):
        """
        {'type': 'boolean'}
        """
        
        if(data is True):
            alpha = "АБВГДЕЁЖЗИЙКЛМНОӨПРСТУҮФХЦЧШЩЪЬЫЭЮЯ"
            VALUE = value.upper()

            if(len(VALUE)!=10 and len(VALUE)!=7):                
                self._error(field, "registernumber")
            elif(len(VALUE)==7):                
                if(not VALUE.isnumeric()):
                    self._error(field, "registernumber")
            elif(len(VALUE)==10):                
                if(VALUE[2:].isdigit()==False or alpha.find(VALUE[0])==-1 or alpha.find(VALUE[1])==-1):                    
                    self._error(field, "registernumber")
           
     
class BuValidator():
    """ JSON өгөгдлийн шалгаж алдааг буцаах """

    def __init__(self,data):
        self.schema = data['fields']
        self.message = data['message']        
        self.v = CustomValidator(self.schema)
        self.errors={}

    def validate(self,data):
        """ JSON өгөгдлийг шалгаж алдааг өгнө 
        Args:
            data: шалгах json өгөгдөл
        """
        
        self.valid = self.v.validate(data)
        
        if(self.valid==False):
            
            for key,value in self.schema.items():
                e = self.v.document_error_tree[key]
                if(e is None): continue
                self.errors[key]=[]
                if(e is not None):
                              
                    for i in e:
                        
                        if(i.field in self.message and i.rule in self.message[i.field]):                            
                            self.errors[key].append(self.message[i.field][i.rule])
                        elif(i.rule==None and len(i.info)==1):
                            self.errors[key].append(self.message[i.field][i.info[0]])
                        else:                            
                            self.errors[key].append("{} field : {}".format(i.schema_path[0],i.schema_path[1]))
                            
            #print(self.errors)  
            raise Exception(self.errors)

    