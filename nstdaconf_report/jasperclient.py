# -*- coding: utf-8 -*-

import requests
import logging
import httplib
import tempfile
from zf import xZipFile
from xml.etree import ElementTree as ET
import json
import re

import os
import sys
import shutil

class JasperClient:
    
    auth = False
    username = False
    password = False
    session = False
    url_rest = False
    path_export_file = False
    temp_path = False
    uri_report = "/rest_v2/reports"
    uri_reportExecutions = "/rest_v2/reportExecutions"
    uri_datasource = "/rest_v2/Datasources"
    uri_resources = "/rest_v2/resources"
    uri_users = "/rest_v2/users"
    uri_permissions = "/rest_v2/permissions"
    uri_export = "/rest_v2/export"
    uri_import = "/rest_v2/import"
    
    def _log(self, success=True, status=200, msg=""):
        if success:
            logging.info("JasperClient::Success %s: %s" % (status, msg))
        else:
            logging.info("JasperClient::Error %s: %s" % (status, msg))
    
    def get_url_import(self):
        return self.url_rest + self.uri_import
    
    def get_url_export(self):
        return self.url_rest + self.uri_export
    
    def get_url_permissions(self):
        return self.url_rest + self.uri_permissions
    
    def get_url_users(self):
        return self.url_rest + self.uri_users
    
    def get_url_report(self):
        return self.url_rest + self.uri_report
    
    def get_url_reportExecutions(self):
        return self.url_rest + self.uri_reportExecutions
    
    
    def get_url_resources(self):
        return self.url_rest + self.uri_resources
    
    def get_url_datasource(self):
        return self.url_rest + self.uri_datasource
    
    
    def __init__(self, url, username, password):
        self.url_rest = url
        self.username = username
        self.password = password
        self.auth = (username, password)    
        self.session = requests.Session()   
        self.login()
        PARENT_ROOT = os.path.dirname(__file__)
        self.temp_path = PARENT_ROOT + "/static/tmp/"

    def login(self):
        r = self.session.get(url=self.url_rest, auth=self.auth)
        if r.status_code == 200:
            self._log(True, r.status_code, "Login Pass.")
            return True
        elif r.status_code == 401:
            self._log(False, r.status_code, "Unauthorized – Empty body.")
            return True
        elif r.status_code == 302:
            self._log(False, r.status_code, "License expired or otherwise not valid.")
            return True
        else:
            self._log(False, r.status_code, "Login Fail.")
            return False
    
    def get_ev(self, res, name):
        tree = ET.fromstring(res.text)
        dataitem = {}
        for item in tree.findall('./*'):
            dataitem[item.tag] = item.text
        if name in dataitem:
            return dataitem[name]
        else:
            return "-"
    
    def get_ev_uri(self, res):
        try:
            tree = ET.fromstring(res.text)
            dataitem = []
            for item in tree.findall('resourceLookup'):
                dataitem.append(item.find('uri').text)
            return dataitem
        except:
            return  False
        
    def get_ev_label(self, res):
        try:
            tree = ET.fromstring(res.text)
            dataitem = []
            for item in tree.findall('resourceLookup'):
                dataitem.append(item.find('label').text)
            return dataitem
        except:
            return  False
            
    def get_ev_users(self, res):
        try:
            tree = ET.fromstring(res.text)
            dataitem = []
            for item in tree.findall('user'):
                dataitem.append(item.find('username').text)
            return dataitem
        except:
            return  False
    
    def run_report(self, report_part, report_format="pdf", params={}, exc_async=False):
        # exc_async=True => not Wait
        # exc_async=False => Wait
        
        url = '%s' % (
            self.get_url_reportExecutions(),
        )
        headers = {"Content-Type": "application/xml"}
        
        _async = 'false'
        if exc_async:
            _async = 'true'

        parameters = ""
        for key, value in params.items():
            parameters += """
                <reportParameter name="%s">
                    <value>%s</value>
                </reportParameter>
            """ % (key,value)
        data = """
                <reportExecutionRequest>
                    <reportUnitUri>%s</reportUnitUri>
                    <async>%s</async>
                    <outputFormat>%s</outputFormat>
                    <parameters>
                        %s
                    </parameters>
                </reportExecutionRequest>
        """ % (report_part, _async, report_format, parameters)

        exportId = False
        requestId = False
        r = self.session.post(url=url, data=data, headers=headers)
        if r.status_code == 200:
            requestId = self.get_ev(r, 'requestId')
            exportId = re.findall("<id>(.*?)</id>", r.content)
            
        if exportId and requestId:
            url = '%s/%s/exports/%s/outputResource' % (
                self.get_url_reportExecutions(),
                requestId, 
                exportId[0]
            )
            r = self.session.get(url=url)
            if r.status_code == 200:
                res = parseMultipart(r)
                return res

#     def run_report(self, report_part, report_format="pdf", params={}):
#         url = '%s%s.%s' % (
#             self.get_url_report(),
#             report_part,
#             report_format
#         )
#         params['format'] = report_format
#         r = self.session.get(url=url, params=params)
#         self._log(True, r.status_code, "run_report()")
#         res = parseMultipart(r)
#         return res
    
    def _format_ds_name(self, ds_name):
        ds_name = ds_name.replace(".", "_")
        ds_name = ds_name.replace("-", "_")
        return ds_name
    
    def search_ds_name(self, ds_name):
        # ================= Search datasource
        url = '%s' % (
            self.get_url_resources()
        )
        params = {'folderUri': ds_name, 'type': 'jdbcDataSource'}
        r = self.session.get(url=url, params=params)
        try:
            datasources_list = self.get_ev_label(r)
            return datasources_list
        except:
            return False
    # ds_uri = '/Datasources/o_nstda/gnc'
    # res_uri = '/Reports/o_nstda/gnc'
    # user_id = 'jasper_gnc'
    # filename = 'o_test_28001'
    def export_service(self, ds_uri, res_uri, user_id, filename):
        uris_list  = False
        datasources_list = False
        resources_list = False
        users_list = False
        filename = 'export_' + filename + ".zip"
        dir_file = self.temp_path + filename
        # ถ้ามีไฟล์เก่าให้ลบไฟล์ออกก่อน
        file_lists = os.listdir(self.temp_path)
        for file_list in file_lists:
            if filename in file_list:
                os.remove(self.temp_path+file_list)

        # ================= Search datasource
        url = '%s' % (
            self.get_url_resources()
        )
        params = {'folderUri': ds_uri, 'type': 'jdbcDataSource'}
        r = self.session.get(url=url, params=params)
        datasources_list = self.get_ev_uri(r)
        # ================= Search resources
        url = '%s' % (
            self.get_url_resources()
        )
        params = {'folderUri': res_uri}
        r = self.session.get(url=url, params=params)
        resources_list = self.get_ev_uri(r)
        # ================= Search users
        url = '%s' % (
            self.get_url_users()
        )
        params = {'search': user_id}
        r = self.session.get(url=url, params=params)
        users_list = self.get_ev_users(r)
        
        uris_list = datasources_list + resources_list
        # =================== Export Service ===============
        phase = False
        export_id = False
        last_status = False
        url = '%s' % (
            self.get_url_export()
        )
        headers = {"Content-Type": "application/json"}
        jsonDict = {}
        if users_list:
            jsonDict['users'] = users_list
        if uris_list:
            jsonDict['uris'] = uris_list
        
        data = json.dumps(jsonDict)
        r = self.session.post(url=url, data=data, headers=headers)
        last_status = r.status_code
        if r.status_code == 200:
            export_id = self.get_ev(r, 'id')
            self._log(True, r.status_code, "Returns a JSON object that gives the ID of the started export operation.")
        else:
            self._log(False, r.status_code, "Export is available only to the system admin user (superuser).")
        
        if last_status == 200:
            while phase != 'finished':
                if export_id:
                    url = '%s/%s/state' % (
                        self.get_url_export(),
                        export_id
                    )
                    r = self.session.get(url=url)
                    phase = self.get_ev(r, 'phase')
    
                if export_id and phase == 'finished':
                    url = '%s/%s/%s' % (
                        self.get_url_export(),
                        export_id,
                        filename
                    )
                    r = self.session.get(url=url)
                    self.export_file_name = filename
                    with open(dir_file, "wb") as f:
                        f.write(r.content)
                    self._log(True, r.status_code, "Download %s Success" % (filename))
            return True
        return False
    
    def import_service(self, filename):
        phase = False
        last_status = False
        import_id = False
        url = '%s' % (
            self.get_url_import()
        )
        
        filename = 'import_' + filename + '.zip'
        
        headers = {
            "Content-Disposition": 'form-data; name="file"; filename="%s"' % (filename),
            "Content-Type": "application/zip",
            "X-Remote=Domain": "true"
        }
        dir_file = self.temp_path + filename
        fileobj = open(dir_file, 'rb')
        params = {
            "update": "true",
            "skipUserUpdate": "false"
        }
        r = self.session.post(url=url, params=params, files={'file': fileobj}, headers=headers)
        last_status = r.status_code
        if r.status_code == 200:
            import_id = self.get_ev(r, 'id')
            self._log(True, r.status_code, "Returns a JSON object that gives the ID of the started import operation.")
        else:
            self._log(False, r.status_code, "Import is available only to the system admin user (superuser).")
        
        while phase not in ['failed', 'finished'] and import_id:
            url = '%s/%s/state' % (
                self.get_url_import(),
                import_id
            )
            r = self.session.get(url=url)
            phase = self.get_ev(r, 'phase')
        if phase == 'failed':
            self._log(False, r.status_code, "Import %s Failed" % (filename))
            return False
        if phase == 'finished':
            self._log(True, r.status_code, "Import %s Success" % (filename))
            return True
    
    # filename = "export_o_test_28016.zip"
    # replace_serv_prd = "o_nstda"
    # replace_serv_test = "o_test_28016"
    # prd_db_url = "o.nstda.or.th"
    # prd_db_port = 29001
    # prd_db_dbname = "odoo"
    # test_db_url = o-test.intra.nstda.or.th
    # test_db_port = 29001
    # test_db_dbname = test
    def modify_zipfile(self, filename, replace_serv_prd, replace_serv_test, prd_db_url, prd_db_port, prd_db_dbname, test_db_url, test_db_port, test_db_dbname):
        conn_url_prd = "%s:%s/%s" % (prd_db_url, prd_db_port, prd_db_dbname)
        conn_url_test = "%s:%s/%s" % (test_db_url, test_db_port, test_db_dbname)
        
        dir_file = self.temp_path + filename
        dir_file_new = dir_file.replace('export_', 'import_').replace('/', '\\')
        if not os.path.exists(dir_file):
            os.remove(dir_file_new)
        shutil.copy(dir_file, dir_file_new)
        
        # replace file
        with xZipFile(dir_file_new, "a") as o:
            for f in o.namelist():
                fname, file_extension = os.path.splitext(f)
                if file_extension:
                    datafile = o.read(f)
                    if datafile.find(replace_serv_prd) > -1:
                        datafile = datafile.replace(replace_serv_prd, replace_serv_test)
                        datafile = datafile.replace(conn_url_prd, conn_url_test)
                        o.writestr(f, datafile)
                        
        # replace add new path & file
        with xZipFile(dir_file_new, "a") as o:
            for f in o.namelist():
                fname, file_extension = os.path.splitext(f)
                if file_extension:
                    datafile = o.read(f)
                    if f.find(replace_serv_prd) > -1:
                        fnew = f.replace(replace_serv_prd, replace_serv_test)
                        o.writestr(fnew, datafile)
                        o.remove_file(f)

        # replace old path
        with xZipFile(dir_file_new, "a") as o:
            for f in o.namelist():
                fname, file_extension = os.path.splitext(f)
                if not file_extension:
                    if f.find(replace_serv_prd) > -1:
                        o.remove_file(f)
        return True
    
    # No access: 0
    # Administer: 1
    # Read-only: 2
    # Read-write: 6
    # Read-delete: 18
    # Read-write-delete: 30
    # Execute-only: 32
    # part_res = ''
    def modify_permissions(self, user_id, part_res):
        url = '%s%s' % (
            self.get_url_permissions(),
            part_res
        )
        headers = {"Content-Type": "application/collection+json"}
        params = {}
        data = """
            {
                "permission" :[
                    {
                        "uri":"%s",
                        "recipient":"user:/%s",
                        "mask":"1"
                    }
                ]
            }
          """ % (part_res, user_id)
        r = self.session.put(url=url, data=data, headers=headers)
        if r.status_code == 400:
            self._log(False, r.status_code, "A recipient or mask is invalid.")
        elif r.status_code == 404:
            self._log(False, r.status_code, "The resource in the URL is invalid.")
        elif r.status_code == 200:
            self._log(True, r.status_code, "The request was successful.")
    
    # user_id = jasper_gnc
    def search_user(self, user_id):
        url = '%s' % (
            self.get_url_users()
        )
        params = {'search': user_id}
        r = self.session.get(url=url, params=params)
        if r.status_code == 404 or r.status_code == 204:
            return False
        else:
            return True
    
    # user_id = jasper_gnc
    # password = jasper_gnc
    def create_user(self, user_id, password):
        if not self.search_user(user_id):
            url = '%s/%s' % (
                self.get_url_users(),
                user_id
            )
            headers = {"Content-Type": "application/json"}
            params = {}
            data = """
                {
                    "enabled":true,
                    "fullName":"%s",
                    "emailAddress":"",
                    "password":"%s",
                    "roles":
                    [{
                        "name":"ROLE_USER",
                        "externallyDefined":false
                    }]
                }
            """ % (user_id, password)
            r = self.session.put(url=url, data=data, params=params, headers=headers)
            if r.status_code == 200 or r.status_code == 201:
                self._log(True, r.status_code, "Created New User: %s Pass." % user_id)
                return True
            else:
                self._log(False, r.status_code, "Created New User: %s Fail!" % user_id)
                return False
        else:
            return False
            
    # res_path '/Reports/Odoo'
    # res_name 'gnc'
    def search_resource(self, res_path, res_name):
        res_path = "%s/%s" % (res_path, res_name)
        url = '%s/%s' % (
            self.get_url_resources(),
            res_path
        )
        params = {'folderUri': res_path, 'type': 'folder'}
        r = self.session.get(url=url, params=params)
        if r.status_code == 404:
            return False
        else:
            return True
    
    # res_path '/Reports/Odoo'
    # res_name 'gnc'
    def create_resource(self, res_path, res_name):
        if not self.search_resource(res_path, res_name):
            res_path = "%s/%s" % (res_path, res_name)
            url = '%s%s' % (
                self.get_url_resources(),
                res_path
            )
            headers = {"Content-Type": "application/repository.folder+json"}
            params = {'overwrite': 'false'}
            data = """
                {
                    "uri" :"%s",
                    "label":"%s",
                    "description":"%s",
                    "permissionMask":"1",
                    "version":"0"
                }
            """ % (res_path, res_name, res_name)
            r = self.session.put(url=url, data=data, params=params, headers=headers)
            if r.status_code == 200:
                self._log(True, r.status_code, "Created New Resource: %s Pass." % res_path)
                return True
            else:
                self._log(False, r.status_code, "Created New Resource: %s Fail!" % res_path)
                return False
        else:
            self._log(False, r.status_code, "Have Resource: %s Create Fail!" % res_path)
            return False
        
    # ds_name = o.nstda
    def search_datasource(self, ds_name):
        ds_name = self._format_ds_name(ds_name)
        url = '%s/%s' % (
            self.get_url_datasource(),
            ds_name
        )
        params = {}
        r = self.session.get(url=url, params=params)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
    
    # ds_uri = o.nstda.or.th/gnc
    # ds_name = o.nstda
    # conn_url = o.nstda
    # conn_port = 29001
    # conn_db = odoo
    # username = odoo
    # password = xxxx
    def create_datasource(self, ds_uri, ds_name, conn_url, conn_port, conn_db, username, password):
        ds_name = self._format_ds_name(ds_name)
        ds_uri = self._format_ds_name(ds_uri)
        datasource = self.search_datasource(ds_name)
        if not datasource:
            logging.info("========== Creating JDBC Data Source ==========")
            url = '%s/Datasources/%s/%s' % (self.get_url_resources(), ds_uri, ds_name)
            headers = {"Content-Type": "application/repository.jdbcDataSource+json"}
            params = {'overwrite': 'false'}
            data = """
                {
                    "uri" :"/Datasources/%s/%s",
                    "label":"%s",
                    "description":"%s",
                    "permissionMask":"1",
                    "version":"0",
                    "driverClass":"org.postgresql.Driver",
                    "username":"%s",
                    "password":"%s",
                    "connectionUrl":"jdbc:postgresql://%s:%s/%s"
                }
            """ % (ds_uri, ds_name, ds_name, ds_name, username, password, conn_url, conn_port, conn_db)
            r = self.session.put(url=url, data=data, params=params, headers=headers)
            if r.status_code == 200:
                self._log(True, r.status_code, "Created New Data Source: %s Pass." % ds_name)
                return True
            else:
                self._log(False, r.status_code, "Created New JDBC Data Source: %s Fail!" % ds_name)
                return False
        else:
            return False
    
def parseMultipart(res):
    contentType = res.headers['content-type']
    return {'content-type': contentType, 'data': res.content}
