from pprint import pprint
from models.Models import Info
from models.base import session, engine
import csv, json

mode = 0
with open('mm.csv', 'r') as f:
  reader = csv.reader(f)
  rnumber_list = list(reader)
i=0
for row in rnumber_list:
  rnumber = row[0]
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
  else:
    continue

  filename = Info.generateFilename()

  info = Info(
    user_uuid='ab6ea344-ccd9-4e87-8e85-2d457a52d77e',
    rnumber=rnumber,
    params = json.dumps(params, ensure_ascii=False),
    filename = filename,
    mode= mode,
    status=Info.STATUS_PENDING
  )
  session.add(info)
  i+=1
  if(i%2==0): session.flush()

session.flush()