#!rest-api/bin/python

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import datetime	

#Create an engine for connecting to SQLIte3, assuming it is in the local folder
e = create_engine('sqlite:///licenseKey.db')

app = Flask(__name__)
api = Api(app)

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
		

#The StoreCodes meta option is normally used for debugging only.
api.add_resource(StoreCodes_Meta, '/starplus/api/v1.0/storecodes')
api.add_resource(GetModules_Meta, '/starplus/api/v1.0/getmodules/<string:store_code>/<string:external_IPAddress>/<string:internal_IPAddress>')


if __name__ == '__main__':
	app.run()		
