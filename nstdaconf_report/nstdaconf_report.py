# -*- coding: utf-8 -*-
# Date             ID         Message
# 1-1-2012         POP-001    Add Class Ineco.Report.Config

import commands
import os
import openerp.report
import tempfile
import time
from mako.template import Template
from mako import exceptions
#import netsvc
from openerp import pooler
#import openerp.pooler
from openerp.report.report_sxw import *
#import addons
from openerp.tools.translate import _
from openerp.osv.osv import except_osv
from openerp.osv import fields,osv
import jasperclient
import base64
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from openerp import api

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class NstdaconfReportParser(report_sxw):
    """Custom class that use webkit to render HTML reports
       Code partially taken from report openoffice. Thanks guys :)
    """

    def __init__(self, name, table, rml=False, parser=rml_parse,
        header=True, store=False, register=True):
        self.localcontext = {}
        report_sxw.__init__(self, name, table, rml, parser,
            header, store, register=register)
    
    def __init__old(self, name, table, rml=False, parser=False, 
        header=True, store=False):
        self.parser_instance = False
        self.localcontext={}
        report_sxw.__init__(self, name, table, rml, parser, 
            header, store)

    def generate_pdf(self, cr, uid, ids, data, report_xml):
        ir_config = self.pool.get('ir.config_parameter')
        base_url = ir_config.get_param(cr, uid, "web.base.url")
        serv = "test"
        if base_url.find('o.nstda.or.th') > 0:
            serv = "pro"
        
        config_url = ir_config.get_param(cr, uid, 'nstdaconf_report.url_%s' % serv)
        config_username = ir_config.get_param(cr, uid, 'nstdaconf_report.jaster_user_%s' % serv)
        config_password = ir_config.get_param(cr, uid, 'nstdaconf_report.jaster_pass_%s' % serv)
        config_parameter_ids = ir_config.get_param(cr, uid, 'nstdaconf_report.parameter_ids')
        
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        m = re.search(p, base_url)
        host = m.group('host')
        host_new = host.replace(".", "_").replace("-", "_")
        
#         if 'nstdaconf.adminmanage' in self.pool:
#             model = report_xml.model.replace('.', '_')
#             model_id = self.pool.get('nstdaconf.adminmanage').search(cr, 1, [('name','=',model)], limit=1)
#             model_obj = self.pool.get('nstdaconf.adminmanage').browse(cr, uid, model_id)
#             
#             config_username = model_obj.jasper_username
#             config_password = model_obj.jasper_password
        rp_path = report_xml.jasper_report_path
        if rp_path.find('#SERVER_URL#') > 0:
            rp_path = rp_path.replace('#SERVER_URL#', host_new)

        #rp_path = "/Reports/o_test_28003_intra_nstda_or_th/gnc"
        
        url = config_url
        user = config_username
        password = config_password
        parameter = config_parameter_ids
        field_pk = report_xml.criteria_field
        report_name = report_xml.report_name
        report_path = "%s/%s" % (rp_path, report_name)
        format = report_xml.jasper_output
        
        if not parameter:
            raise osv.except_osv(_('Warning !'), _('Report requried parameter config name.'))
        
        if not ids:
            raise osv.except_osv(_('Warning !'), _('Report requried data["%s"].' % parameter))

        report_param = {}
        if url and user and password and report_path:
            if field_pk:
                criteries = field_pk + ' in '+ str(tuple(sorted(ids)))
                criteries = criteries.replace(',)',')')
                if parameter:
                    report_param[parameter] = criteries
            if data:
                for key, value in data.iteritems():    # for name, age in dictionary.iteritems():  (for Python 2.x)
                    report_param[key] = value
           
            j = jasperclient.JasperClient(url,user,password)
            a = j.run_report(report_path, format, report_param) # {'pick_ids': criteries})
            if 'data' in a:
                if a['data'].find('errorDescriptor') > 0:
                    raise osv.except_osv(_('Error !'), _('%s' % a['data']))
                else:
                    buf = StringIO()
                    buf.write(a['data'])
                    pdf = buf.getvalue()
        else:
            raise osv.except_osv(_('Warning !'), _('Please fill data in Report Path and Criteria.'))

        return pdf    

    # override needed to keep the attachments' storing procedure
    def create_single_pdf(self, cursor, uid, ids, data, report_xml, context=None):
        """generate the PDF"""
        
        if context is None:
            context={}

        if report_xml.report_type != 'jasperserver_rest_v2':
            return super(NstdaconfReportParser,self).create_single_pdf(cursor, uid, ids, data, report_xml, context=context)

        self.parser_instance = self.parser(
                                            cursor,
                                            uid,
                                            self.name2,
                                            context=context
                                        )

        self.pool = pooler.get_pool(cursor.dbname)
        objs = self.getObjects(cursor, uid, ids, context)
        self.parser_instance.set_context(objs, data, ids, report_xml.report_type)

        pdf = self.generate_pdf(cursor, uid, ids, data, report_xml)
        return (pdf, report_xml.jasper_output)


    def create(self, cursor, uid, ids, data, context=None):
        """We override the create function in order to handle generator
           Code taken from report openoffice. Thanks guys :) """
        pool = pooler.get_pool(cursor.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cursor, uid,
                [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:
            
            report_xml = ir_obj.browse(
                                        cursor, 
                                        uid, 
                                        report_xml_ids[0], 
                                        context=context
                                    )
            report_xml.report_rml = None
            report_xml.report_rml_content = None
            report_xml.report_sxw_content_data = None
            report_rml.report_sxw_content = None
            report_rml.report_sxw = None
        else:
            return super(NstdaconfReportParser, self).create(cursor, uid, ids, data, context)
        if report_xml.report_type != 'jasperserver_rest_v2' :
            return super(NstdaconfReportParser, self).create(cursor, uid, ids, data, context)
        result = self.create_source_pdf(cursor, uid, ids, data, report_xml, context)
        if not result:
            return (False,False)
        return result

#POP-001
class nstdaconf_report_config(osv.osv):
    
    _name = "nstdaconf.report.config"
    _description = "Nstdaconf Report Configuration"
    _columns = {
        'name': fields.char('Name', size=100),
        'report_id': fields.char('Report ID', size=100),
        'description': fields.char('Description',size=100),
        'type': fields.char('Report Type', size=50),
        'host': fields.char('Jasper Server Host', size=100),
        'report_user': fields.char('Jasper Uer Name', size=20),
        'report_password': fields.char('Jasper Password', size=20),
        'active': fields.boolean('Active')
    }
    _defaults = {
        'active': True,
        'host': 'localhost',
        'report_user': 'jasperadmin',
        'report_password': 'jasperadmin'
    }
    _order = 'name'
    