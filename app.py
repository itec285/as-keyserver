#!rest-api/bin/python

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import datetime, socket
import sys

#Create an engine for connecting to SQLIte3, assuming it is in the local folder
e = create_engine('sqlite:///licenseKey.db')
logDB = create_engine('sqlite:///requestLog.db')

app = Flask(__name__)
api = Api(app)

def get_askey(host, port, serialNumber, modules, numberOfClients, store_code):
#This function's job is to take a key request (typically from GetKey) and parse the data, then open a 
# socket connection to the keyserver, decode it and return the result.  Note that host and port are defined in GetKey
# and passed as arguments to this function.

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
#Returns a list of all possible storecodes.  This is for testing purposes only and is blocked except
# in cases where the request is coming from an internal address.
	def get(self):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()
		
		#Restrict access to this function by detected (real) IP
		if (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
		
			#perform query and return JSON data
			query = conn.execute("Select distinct STORECODE from Modules")
			queryResult = [i[0] for i in query.cursor.fetchall()]
			
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'StoreCodes'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, RealIPAddress) VALUES(?,?,?)", (now, requestType, real_IPAddress))
					
			return {'StoreCodes': queryResult}
			#return {'StoreCodes': [i[0] for i in query.cursor.fetchall()]}
		else:
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'StoreCodes'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, RealIPAddress) VALUES(?,?,?)", (now, requestType, real_IPAddress))

			#If we're in this section, the request was invalid due to wrong external IP or detected (real) IP.  Return an error code.
			return "ERROR: Invalid Request - bad IP"

class GetModules_Meta(Resource):
#This returns a boolean list of what modules are turned on for a given store.  
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()
		
		#Restrict access to this function by (stated 'external') IP and detected (real) IP
		if (external_IPAddress == '24.244.1.123') and (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):		
		
			#Perform query and return JSON data
			query = conn.execute("SELECT * FROM Modules WHERE StoreCode =?", (store_code.upper()))
			queryResult = query.cursor.fetchall()[0]
			
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
				
			return jsonify({'Data': queryResult})
		else:
			#Before we return the error, log the request.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If we're in this section, the request was invalid due to wrong external IP or detected (real) IP.  Return an error code.		
			if (external_IPAddress != '24.244.1.123'):
				return "ERROR: Invalid Request - bad external IP"
			
			if not (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
				return "ERROR: Invalid Request - bad IP"

class GetVar_Meta(Resource):
#This returns a value of a VAR for a given store.  
	def get(self,store_code):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()
				
		#Perform query and return JSON data
		query = conn.execute("SELECT * FROM Reseller WHERE StoreCode =?", (store_code.upper()))

		try:
			queryResult = query.cursor.fetchall()[0]
			#print (str(queryResult))
		except IndexError:
			print('\n Error - query of VAR failed. Returning "DIRECT"  \n\n')
			#return ('Error: invalid store')
			queryResult = [9999, store_code.upper(), 'DIRECT']
		
		#Format the data in a way Blake likes.  This is the cheap way to do it, but fastest since we know the order..
		returnDict = {
			"row" : str(queryResult[0]),
			"storecode" : str(queryResult[1]),
			"var" : str(queryResult[2])
		}
		
		print(returnDict)

		#Before we return the request, log the request and the result.
		now = datetime.datetime.now()
		requestType = 'GetVar'
		query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, RealIPAddress) VALUES(?,?,?,?)", (now, requestType, store_code.upper(), real_IPAddress))
		
		return 	jsonify(returnDict)
		#return jsonify({'Data': queryResult})

class GetModules2_Meta(Resource):
#This returns a formatted list of what modules are turned on for a given store.  It is similar in nature to GetModules
# but formats the data in an easier to use format. 
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()

		#Restrict access to this function by (stated 'external') IP and detected (real) IP
		if (external_IPAddress == '24.244.1.123') and (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
			
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
			if (queryresult[19] == 1): returnString += "| Gaspump is on"
			if (queryresult[20] == 1): returnString += "| PDALineBusting is on"
			if (queryresult[21] == 1): returnString += "| Electronic Shelf Label (2023) is on"
			if (queryresult[22] == 1): returnString += "| Inactive is on"
			if (queryresult[23] == 1): returnString += "| Warehouse (2023) is on"
			if (queryresult[24] == 1): returnString += "| AdvancedGWP is on"
			if (queryresult[25] == 1): returnString += "| Rentals (2023) is on"
			if (queryresult[26] == 1): returnString += "| Kiosk is on"
			if (queryresult[27] == 1): returnString += "| Dashboard is on"
			returnString += "| Total number of clients: " + str(queryresult[28]) + ". Includes a 'fudge' factor of 3 and one till/workstation each for the basic package. So all stores start at 5 plus any additional tills and workstations.  Base store + 1 till = 6." 

			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If they've made it here, it was a valid request.  Return the full returnString we just built.
			return returnString
			#return jsonify({'Data': returnString})
		else:
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If we're in this section, the request was invalid due to wrong external IP or detected (real) IP.  Return an error code.		
			if (external_IPAddress != '24.244.1.123'):
				return "ERROR: Invalid Request - bad external IP"
			
			if not (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
				return "ERROR: Invalid Request - bad IP"

class GetModules3_Meta(Resource):
#This returns a formatted list of what modules are turned on for a given store.  It is similar in nature to GetModules2
# but adds a till and workstation count at the end. 
	def get(self,store_code, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()

		#Restrict access to this function by (stated 'external') IP and detected (real) IP
		if (external_IPAddress == '24.244.1.123') and (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
			
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
			if (queryresult[19] == 1): returnString += "| Gaspump is on"
			if (queryresult[20] == 1): returnString += "| PDALineBusting is on"
			if (queryresult[21] == 1): returnString += "| Electronic Shelf Label (2023) is on"
			if (queryresult[22] == 1): returnString += "| Inactive is on"
			if (queryresult[23] == 1): returnString += "| Warehouse (2023) is on"
			if (queryresult[24] == 1): returnString += "| AdvancedGWP is on"
			if (queryresult[25] == 1): returnString += "| Rentals (2023) is on"
			if (queryresult[26] == 1): returnString += "| Kiosk is on"
			if (queryresult[27] == 1): returnString += "| Dashboard is on"
			returnString += "| Total number of clients: " + str(queryresult[28]) + ". Includes a 'fudge' factor of 3 and one till/workstation each for the basic package. So all stores start at 5 plus any additional tills and workstations.  Base store + 1 till = 6." 
			returnString += "| Total number of tills: " + str(queryresult[29]) 
			returnString += "| Total number of workstations: " + str(queryresult[30]) 
			

			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If they've made it here, it was a valid request.  Return the full returnString we just built.
			return returnString
			#return jsonify({'Data': returnString})
		else:
			#Before we return the request, log the request and the result.
			now = datetime.datetime.now()
			requestType = 'GetModules2'
			query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?)", (now, requestType, store_code.upper(), external_IPAddress, internal_IPAddress, real_IPAddress))
			
			#If we're in this section, the request was invalid due to wrong external IP or detected (real) IP.  Return an error code.		
			if (external_IPAddress != '24.244.1.123'):
				return "ERROR: Invalid Request - bad external IP"
			
			if not (real_IPAddress.startswith('10.10.') or real_IPAddress.startswith('172.16.') or real_IPAddress.startswith('127.0.0.1')):
				return "ERROR: Invalid Request - bad IP"

			
class GetKey_Meta(Resource):
#This returns an activation key given a store code and serial number.  It calls get_askey to actually call the server.
	def get(self,store_code, serialNumber, external_IPAddress, internal_IPAddress):
		
		real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		print ('-------------------\n New Request from: ' + real_IPAddress)
		
		print ('\n\n\n#######    NEW KEY REQUEST - ' +  str(datetime.datetime.now()) + '    #######')
		
		#Connect to the databases
		conn = e.connect()
		logconn = logDB.connect()
		
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
		query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, SerialNumber, ExternalIPAddress, InternalIPAddress, RealIPAddress) VALUES(?,?,?,?,?,?,?)", (now, requestType, store_code.upper(), serialNumber, external_IPAddress, internal_IPAddress, real_IPAddress))
				
		#Send an answer back.  Note that there's a lot of ways to do this below.  I worked with Aaron 
		# to come up with the best way to send data back for him.
		return str(myanswer[1])
		#return jsonify(myanswer)
		#return jsonify({'Data': myanswer})
		#return jsonify({'Data':myanswer[1]})
		
class SendModules_Meta(Resource):
#This is the opposite of many of the functions and actually takes data from a store via a POST request.  It then records
# the modules the store reports in a 'ReportedModules' table.
#
# Aug 13, 2018 - Changed this to move data to the RequestLog DB rather than the LicenseKeyDB.
#  This is because the CRM server may clobber data in the LicenseKeyDB when it moves that DB in every hour.
		def post(self):
			real_IPAddress = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
			print ('-------------------\n New Request from: ' + real_IPAddress)	
			print ('    [--Start of Request Headers--] \n' + str(request.headers) + '    [--End of Request Headers--] \n')	
			print ('    [--Start of Request Text--] \n' + str(request.data.decode('utf-8')) + '    [--End of Request Text--] \n')	
			
			#Connect to the databases
			# Aug 13, 2018 - Changed this to move data to the RequestLog DB rather than the LicenseKeyDB.
			#  This is because the CRM server may clobber data in the LicenseKeyDB when it moves that DB in every hour.
			#conn = e.connect()
			conn = logDB.connect()
			logconn = logDB.connect()
			
			
			if request.headers['Content-Type'] == 'text/plain':
				
				#Get the contents of what I was sent
				contents = request.data.decode('utf-8')
				#Now, split it based on comma.  TODO: May be problematic in the case where commas are preceeded by an escape character.
				contents = contents.split(",")
								
				store_code = contents[0].upper()
				
				#Get the individual modules from the contents (note there are 26 modules including module 0
				module0, module1, module2, module3, module4, module5, module6, module7, module8, module9, \
				module10, module11, module12, module13, module14, module15, module16, module17, module18, \
				module19, module20, module21, module22, module23, module24, module25 = contents[1:27] 
								
				numberOfClients = contents[27]
				serialNumber = contents[28]
				version = contents[29]
				location0Name = contents[30]
				location0Address = contents[31]
				location0Phone = contents[32]
				
				#For debug purposese only
				'''
				returnString = "Store Code and modules 0 and 25: " + " " + store_code + " " + module0 + " " + module25 			
				returnString += "|  Number of Clients:" + numberOfClients 
				returnString += "|  Serial Number:" + serialNumber 
				returnString += "|  Version:" + version 
				returnString += "|  Location 0 Name:" + location0Name 
				returnString += "|  Location 0 Address:" + location0Address 
				returnString += "|  Location 0 Phone:" + location0Phone 
				return returnString
				'''
				
				#Insert the data that we determined above into the ReportedModules Table in the licenseKey.db file
				query = conn.execute("INSERT INTO ReportedModules (StoreCode, Module0, Module1, Module2, Module3, \
				Module4, Module5, Module6, Module7, Module8, Module9, Module10, Module11, Module12, Module13, \
				Module14, Module15, Module16, Module17, Module18, Module19, Module20, Module21, Module22, Module23, \
				Module24, Module25, NumberOfClients, SerialNumber, Version, Location0Name, Location0Address, Location0Phone) \
				VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (store_code, \
				module0, module1, module2, module3, module4, module5, module6, module7, module8, module9, \
				module10, module11, module12, module13, module14, module15, module16, module17, module18, \
				module19, module20, module21, module22, module23, module24, module25, numberOfClients, serialNumber, \
				version, location0Name, location0Address, location0Phone))
				
				returnString = {'data':query.lastrowid}
				
				#Before we do anything else, log the request and the result.
				now = datetime.datetime.now()
				requestType = 'SendModules'
				query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, SerialNumber, RealIPAddress, RequestHeaders, RequestData) VALUES(?,?,?,?,?,?,?)", (now, requestType, store_code.upper(), serialNumber, real_IPAddress,str(request.headers),str(request.data.decode('utf-8'))  ))
						
				return returnString
				
			else:
				now = datetime.datetime.now()
				requestType = 'SendModules'
				query = logconn.execute("INSERT INTO RequestLog(DateTime, RequestType, StoreCode, SerialNumber, RealIPAddress, RequestHeaders, RequestData) VALUES(?,?,?,?,?,?,?)", (now, requestType, 'INVALID CONTENT TYPE', '', real_IPAddress,str(request.headers),str(request.data.decode('utf-8')) ))
				return "ERROR: Invalid Content-Type"
				
				
#The StoreCodes meta option is normally used for debugging only.
api.add_resource(StoreCodes_Meta, '/starplus/api/v1.0/storecodes')
api.add_resource(GetModules_Meta, '/starplus/api/v1.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetModules2_Meta, '/starplus/api/v2.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetModules3_Meta, '/starplus/api/v3.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetKey_Meta, '/starplus/api/v1.0/getkey/<string:store_code>/<string:serialNumber>/<string:external_IPAddress>/<string:internal_IPAddress>')
api.add_resource(GetVar_Meta, '/starplus/api/v1.0/getvar/<string:store_code>')
api.add_resource(SendModules_Meta, '/starplus/api/v1.0/sendmodules')

if __name__ == '__main__':
#	app.run()		
# Do the below for the app to run from external hosts (Dangerous)
	app.run(host='0.0.0.0')
