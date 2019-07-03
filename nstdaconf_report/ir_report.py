# -*- coding: utf-8 -*-
import openerp

from openerp.osv import osv, fields, orm
from openerp import netsvc
from nstdaconf_report import NstdaconfReportParser
from openerp.report.report_sxw import rml_parse

def register_report(name, model, tmpl_path, parser=rml_parse):
    "Register the report into the services"
    name = 'report.%s' % name
    if netsvc.Service._services.get(name, False):
        service = netsvc.Service._services[name]
        if isinstance(service, NstdaconfReportParser):
            #already instantiated properly, skip it
            return
        if hasattr(service, 'parser'):
            parser = service.parser
        del netsvc.Service._services[name]
    NstdaconfReportParser(name, model, tmpl_path, parser=parser)

class ir_actions_report_xml(orm.Model):

    _inherit = 'ir.actions.report.xml'
    _columns = {
        'name': fields.char('Filename for Download', required=True, translate=True),
        'report_name': fields.char('Report Name', required=True, help="For QWeb reports, name of the template used in the rendering. The method 'render_html' of the model 'report.template_name' will be called (if any) to give the html. For RML reports, this is the LocalService name."),
        
        'jasper_url': fields.char('Jasper Server URL', size=254),
        'jasper_report_path': fields.char('Jaser Server Report Path (Parent Folder)', size=254),
        'jasper_username': fields.char('User Name', size=20),
        'jasper_password': fields.char('Password', size=20),
        'criteria_field': fields.char('Criteria Field', size=100),
        'parameter_name': fields.char('Jasper Parameter Name', size=100),
        'report_type': fields.selection([('qweb-pdf', 'PDF'),
                    ('qweb-html', 'HTML'),
                    ('controller', 'Controller'),
                    ('pdf', 'RML pdf (deprecated)'),
                    ('sxw', 'RML sxw (deprecated)'),
                    ('webkit', 'Webkit (deprecated)'),
                    ('jasperserver_rest_v2', 'Jasperserver RESTv2'),
                    ], 'Report Type', required=True, help="HTML will open the report directly in your browser, PDF will use wkhtmltopdf to render the HTML into a PDF file and let you download it, Controller allows you to define the url of a custom controller outputting any kind of report."),
    }
    
    _defaults = {
        'jasper_url': 'https://pabi2report-test.intra.nstda.or.th/jasperserver/rest_v2/reports',
    }
    
    def _lookup_report(self, cr, name):
        """
        Look up a report definition.
        """
        import operator
        import os
        opj = os.path.join

        # First lookup in the deprecated place, because if the report definition
        # has not been updated, it is more likely the correct definition is there.
        # Only reports with custom parser specified in Python are still there.
        if 'report.' + name in openerp.report.interface.report_int._reports:
            new_report = openerp.report.interface.report_int._reports['report.' + name]
            if not isinstance(new_report, NstdaconfReportParser):
                new_report = None
        else:
            cr.execute("SELECT * FROM ir_act_report_xml WHERE report_name=%s and report_type=%s", (name, 'jasperserver_rest_v2'))
            r = cr.dictfetchone()
            if r:
                if r['parser']:
                    parser = operator.attrgetter(r['parser'])(openerp.addons)
                    kwargs = { 'parser': parser }
                else:
                    kwargs = {}

                new_report = NstdaconfReportParser('report.'+r['report_name'],
                    r['model'], opj('addons',r['report_rml'] or '/'),
                    header=r['header'], register=False, **kwargs)
            else:
                new_report = None

        if new_report:
            return new_report
        else:
            return super(ir_actions_report_xml, self)._lookup_report(cr, name)

#     Example Report Jakkrich.cha
    def start_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        params = {}
        params['ids'] = [2392,2396,239,240,2982,1357,3120,241,242]
        params['aaa'] = 'aaa'
        params['bbb'] = 'bbb'
        params['ccc'] = 'ccc'
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': "res_users_test_report_pdf",
            'datas': params,
        }
        