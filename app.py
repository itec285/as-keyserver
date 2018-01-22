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
		query = conn.execute("Select distinct STORECODE from modules")
		return {'StoreCodes': [i[0] for i in query.cursor.fetchall()]}

api.add_resource(StoreCodes_Meta, '/starplus/api/v1.0/storecodes')

if __name__ == '__main__':
	app.run()		
