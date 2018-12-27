# -*- coding: utf-8 -*-
"""
For only connection. You can change config file name from keyword
"Config file name" in comment line, ex: migration.conf.
In config file has hostname, port, database, login, password, user_id and
protocal.

Prepare config file
1. migration_remote.conf (For server pre-production).
2. migration.conf (For server localhost).
"""
import openerplib
import ConfigParser
import os
import xmlrpclib
# Config file name
conf = 'migration.conf'


def get_connection(config_file):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = '%s/%s' % (file_dir, config_file)
    config = ConfigParser.ConfigParser()
    config.readfp(open(file_path))
    hostname = config.get('server', 'hostname')
    port = int(config.get('server', 'port'))
    database = config.get('server', 'database')
    login = config.get('server', 'login')
    password = config.get('server', 'password')
    user_id = int(config.get('server', 'user_id'))
    protocol = config.get('server', 'protocol')
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol=protocol, user_id=user_id)
    return connection

def get_connection_xmlrpc(config_file):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = '%s/%s' % (file_dir, config_file)
    config = ConfigParser.ConfigParser()
    config.readfp(open(file_path))
    hostname = config.get('server', 'hostname')
    port = int(config.get('server', 'port'))
    database = config.get('server', 'database')
    login = config.get('server', 'login')
    password = config.get('server', 'password')
    user_id = int(config.get('server', 'user_id'))
    protocol = config.get('server', 'protocol')
    url = 'https://' + hostname
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(database, login, password, {})
    return models, common, uid, database, password


def get_data(xmlrpc_database,xmlrpc_uid,xmlrpc_password,ModelTarget, id):
	section = False
	project = False
	invest_asset = False
	invest_construction_phase = False
	personnel_costcenter = False
	data = xmlrpc_models.execute_kw(xmlrpc_database,
		xmlrpc_uid,
		xmlrpc_password,
		ModelTarget, 'read',
		[id],
		{'fields': ['section_id', 'project_id', 'invest_asset_id', 'invest_construction_phase_id', 'personnel_costcenter_id']})
	if data['section_id']:
		section = data['section_id'][1]
	if data['project_id']:
		project = data['project_id'][1]
	if data['invest_asset_id']:
		invest_asset = data['invest_asset_id'][1]
	if data['invest_construction_phase_id']:
		invest_construction_phase = data['invest_construction_phase_id'][1]			
	if data['personnel_costcenter_id']:
		personnel_costcenter = data['personnel_costcenter_id'][1]	
	return section, project, invest_asset, invest_construction_phase, personnel_costcenter

connection = get_connection(conf)
connection.check_login()

xmlrpc_models, xmlrpc_common, xmlrpc_uid, xmlrpc_database, xmlrpc_password = get_connection_xmlrpc(conf)