#!/usr/bin/env python

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import power_snmp


app = Flask(__name__)

HOST_NAME = 'apc'

# when linking to the main page, don't use trailing slash
# correct example: http://host:8080
# reason: matching config between route below and the apache.conf file
@app.route("/")
def index():
	apc = power_snmp.APC9210(HOST_NAME)
	return render_template('index.html', apc = apc)

@app.route("/change_status", methods=['POST',])
def change_status():
	apc = power_snmp.APC9210(HOST_NAME)
	print request.form
	# dirty and unsanitary
	getattr(apc, request.form['new_status'].lower().strip())(request.form['port_number'])
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.debug = True
	app.run()
