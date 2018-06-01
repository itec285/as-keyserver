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
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the database
		conn = e.connect()
		#perform query and return JSON data
		query = conn.execute("Select distinct STORECODE from Modules")
		queryResult = [i[0] for i in query.cursor.fetchall()]
		
		#Before we return the request, log the request and the result.
		now = datetime.datetime.now()
		requestType = 'StoreCodes'
		query = conn.execute("INSERT INTO RequestLog(DateTime, RequestType, RealIPAddress) VALUES(?,?,?)", (now, requestType, real_IPAddress))
				
		return {'StoreCodes': queryResult}
		#return {'StoreCodes': [i[0] for i in query.cursor.fetchall()]}

class GetModules_Meta(Resource):
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the database
		conn = e.connect()
		#Perform query and return JSON data
		query = conn.execute("SELECT * FROM Modules WHERE StoreCode =?", (store_code.upper()))
		queryResult = query.cursor.fetchall()[0]
		
		#Before we return the request, log the request and the result.
		now = datetime.datetime.now()
		requestType = 'GetModules'
		query = conn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
		return jsonify({'Data': queryResult})

class GetModules2_Meta(Resource):
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		if (external_IPAddress == '24.244.1.123'):
			#Connect to the database
			conn = e.connect()
			#Perform query and return JSON data
			query = conn.execute("SELECT * FROM Modules WHERE StoreCode =?", (store_code.upper()))

			#The above query will actually return a list of lists.  Return just the first list and put into the var result
			queryresult = query.cursor.fetchall()[0]

			#Start building the returnstring
			returnString = "Storecode " + str(queryresult[1]) 
			if (queryresult[2] == 1): returnString += ": Basic is on" 
			if (queryresult[3] == 1): returnString += "| Star-Link Integration is on" 
			if (queryresult[4] == 1): returnString += "| A/R is on" 
			if (queryresult[5] == 1): returnString += "| Loyalty is on"
			if (queryresult[6] == 1): returnString += "| Signs&Labels is on"
			if (queryresult[7] == 1): returnString += "| AdvancedInvControl is on"
			if (queryresult[8] == 1): returnString += "| Scientific is on"
			if (queryresult[9] == 1): returnString += "| Purchasing&Receiving is on"
			if (queryresult[10] == 1): returnString += "| Multi-Store is on"
			if (queryresult[11] == 1): returnString += "| Wireless is on"
			if (queryresult[12] == 1): returnString += "| Replenishment is on"
			if (queryresult[13] == 1): returnString += "| OrderDesk is on"
			if (queryresult[14] == 1): returnString += "| Delivery is on"
			if (queryresult[15] == 1): returnString += "| AdvancedSigCap is on"
			if (queryresult[16] == 1): returnString += "| Accounting is on"
			if (queryresult[17] == 1): returnString += "| InterStoreTransfer is on"
			if (queryresult[18] == 1): returnString += "| Fingerprint is on"
			if (queryresult[19] == 1): returnString += "| GasPump is on"
			if (queryresult[20] == 1): returnString += "| PDALineBusting is on"
			if (queryresult[21] == 1): returnString += "| Inactive is on"
			if (queryresult[22] == 1): returnString += "| Inactive is on"
			if (queryresult[23] == 1): returnString += "| Inactive is on"
			if (queryresult[24] == 1): returnString += "| AdvancedGWP is on"
			if (queryresult[25] == 1): returnString += "| Rentals is on"
			if (queryresult[26] == 1): returnString += "| Kiosk is on"
			if (queryresult[27] == 1): returnString += "| Dashboard is on"
			returnString += "| Total number of clients: " + str(queryresult[28]) + ". Includes a 'fudge' factor of 3 and one till/workstation each for the basic package. So all stores start at 5 plus any additional tills and workstations.  Base store + 1 till = 6." 

			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = conn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If they've made it here, it was a valid request.  Return the full returnString we just built.
			return returnString
			#return jsonify({'Data': returnString})
		else:
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = conn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If we're in this section, the request was invalid due to wrong external IP.  Return an error code.		
			return "ERROR: Invalid Request"
			
class GetKey_Meta(Resource):
	def get(self,store_code, serialNumber, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
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
			return ('ERROR:Invalid Store Code')
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
		
		#Now, go out and fetch the key from the key server.
		myanswer = get_askey(host, port, serialNumber, modules, numberOfClients, store_code)
		#Remove trailing newline from the key portion of the answer
		myanswer[1] = str(myanswer[1]).rstrip()
		
		#Before we return the request, log the request and the result.
		now = datetime.datetime.now()
		requestType = 'GetKey'
		query = conn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, SerialNumber, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?,?)", (now, requestType, store_code.upper(), serialNumber, external_IPAddress, internal_IPAddress, real_IPAddress))
				
		#Send an answer back.  Note that there's a lot of ways to do this below.  I worked with Aaron 
		# to come up with the best way to send data back for him.
		return str(myanswer[1])
		#return jsonify(myanswer)
		#return jsonify({'Data': myanswer})
		#return jsonify({'Data':myanswer[1]})
		
		

#The StoreCodes meta option is normally used for debugging only.
api.add_resource(StoreCodes_Meta, '/starplus/api/v1.0/storecodes')
api.add_resource(GetModules_Meta, '/starplus/api/v1.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetModules2_Meta, '/starplus/api/v2.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetKey_Meta, '/starplus/api/v1.0/getkey/<string:store_code>/<string:serialNumber>/<string:external_IPAddress>/<string:internal_IPAddress>')


if __name__ == '__main__':
#	app.run()		
# Do the below for the app to run from external hosts (Dangerous)
	app.run(host='0.0.0.0')
