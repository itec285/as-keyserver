#!/usr/bin/env python

#Imports
import socket

#Define Variables------
host = '10.10.3.44'
port = 12345
serialNumber = '7777'
modules = '1011100010000000010000001'
numberOfClients = '10'
storeCode = 'ivan01'
#----------------------

def get_askey(host, port, serialNumber, modules, numberOfClients, storeCode):
	#Create the socket
	s = socket.socket()
	s.connect((host, port))
	
	#dataToSendList = [serialNumber, modules, numberOfClients, storeCode]
	#Convert the list from format:
	#  ['7777', '1011100010000000010000001', '10', 'ivan01'] to 
	#  7777,1011100010000000010000001,10,ivan01 and add a newline
	#dataToSend = ','.join(map(str,dataToSendList)) + '\n'
	
	#The above can be done with the below method instead.  Skips the step of making a list but harder to read..
	dataToSend = ','.join(map(str,('GenerateKey',serialNumber, modules, numberOfClients, storeCode))) + '\n'
	
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

	
get_askey(host, port, serialNumber, modules, numberOfClients, storeCode)
