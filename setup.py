from models.base import Base, engine
from models.Models import User, Info
from sqlalchemy.schema import CreateTable
from pprint import pprint


'''if(User.__table__.exists() is True):
    User.__table__.drop()
User.__table__.create()

if(Info.__table__.exists() is True):
    Info.__table__.drop()
Info.__table__.create()'''