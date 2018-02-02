#!rest-api/bin/python

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import datetime, socket

#Create an engine for connecting to SQLIte3, assuming it is in the local folder
e = create_engine('sqlite:///licenseKey.db')

app = Flask(__name__)
api = Api(app)

def get_askey(host, port, serialNumber, modules, numberOfClients, store_code):
	#Create the socket
	s = socket.socket()
	s.connect((host, port))
	
	#dataToSendList = [serialNumber, modules, numberOfClients, storeCode]
	#Convert the list from format:
	#  ['7777', '1011100010000000010000001', '10', 'ivan01'] to 
	#  7777,1011100010000000010000001,10,ivan01 and add a newline
	#dataToSend = ','.join(map(str,dataToSendList)) + '\n'
	
	#The above can be done with the below method instead.  Skips the step of making a list but harder to read..
	dataToSend = ','.join(map(str,('GenerateKey',serialNumber, modules, numberOfClients, store_code))) + '\n'
	
	#print (dataToSend)
	print ('Sending the following: ' + dataToSend)
	
	# In python3, you have to encode the message before you send it.  In python2 you could have just used: > s.send(dataToSend)
	s.send(dataToSend.encode('utf-8'))
	answer = s.recv(1024).decode('utf-8')
	answer = answer.split(",")
	#print (answer)
	if (answer[0] == '0'):
		print ('The Key is: ' + answer[1])
	else:
		print ('Error :' + str(answer))
	s.close
	return answer

class StoreCodes_Meta(Resource):
	def get(self):
		#Connect to the database
		conn = e.connect()
		#perform query and return JSON data
		query = conn.execute("Select distinct STORECODE from Modules")
		return {'StoreCodes': [i[0] for i in query.cursor.fetchall()]}

class GetModules_Meta(Resource):
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		#Connect to the database
		conn = e.connect()
		#Perform query and return JSON data
		query = conn.execute("SELECT * FROM Modules WHERE StoreCode =?", (store_code.upper()))
		return jsonify({'Data': query.cursor.fetchall()})

class GetKey_Meta(Resource):
	def get(self,store_code, serialNumber, external_IPAddress, internal_IPAddress):
		print ('\n\n\n#######    NEW KEY REQUEST - ' +  str(datetime.datetime.now()) + '    #######')
		
		#Connect to the database
		conn = e.connect()
		#Perform query and return row with that store's data
		query = conn.execute("SELECT * FROM Modules WHERE StoreCode =?", (store_code.upper()))
		queryResult = (query.fetchone())
		
		#Make sure that a valid row in the DB exists.
		if str(queryResult) == 'None':
			#Invalid store code, log the error and return 'Invalid Store Code'			
			print ('Error, supplied store_code ' + store_code.upper() + ' did not match any records')
			return ('Invalid Store Code')
		else:
			print ('Returned data was ' + str(queryResult) )
		
		#Convert 
		#	FROM	(11, 'ABCP01', 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
		#   TO		10101101000000000000000001      #Just the module columns, no spaces...
		moduleListTmp = queryResult[2:]
		#Convert from a tuple list of numbers to a string.  See stackoverflow.com/questions/10880813/
		modules = ''.join(str(m) for m in moduleListTmp)
		print ('My modules are ' + modules)
			
		#Define Variables------
		host = '10.10.3.44'
		port = 12345
		#serialNumber = '7777'
		#modules = '1011100010000000010000001'
		numberOfClients = '10'
		#store_code = 'ivan01'
		#----------------------
		
		myanswer = get_askey(host, port, serialNumber, modules, numberOfClients, store_code)
		#Remove trailing newline from the key portion of the answer
		myanswer[1] = str(myanswer[1]).rstrip()
		
		#return jsonify(myanswer)
		#return jsonify({'Data': myanswer})
		#return str(myanswer[1])
		return jsonify({'Data':myanswer[1]})

#The StoreCodes meta option is normally used for debugging only.
api.add_resource(StoreCodes_Meta, '/starplus/api/v1.0/storecodes')
api.add_resource(GetModules_Meta, '/starplus/api/v1.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetKey_Meta, '/starplus/api/v1.0/getkey/<string:store_code>/<string:serialNumber>/<string:external_IPAddress>/<string:internal_IPAddress>')


if __name__ == '__main__':
#	app.run()		
# Do the below for the app to run from external hosts (Dangerous)
	app.run(host='0.0.0.0')
