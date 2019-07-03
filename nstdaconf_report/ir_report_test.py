# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import jasperclient
import re

class ir_actions_report_xml(models.Model):
    
    _inherit = 'ir.actions.report.xml'
    
    # https://o.nstda.or.th => o.nstda.or.th
    def get_host_name(self):
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        m = re.search(p, base_url)
        host = m.group('host')
        return host
    
    # https://o.nstda.or.th => o_nstda_or_th
    def get_host_name_new(self):
        host = self.get_host_name()
        host_new = host.replace(".", "_").replace("-", "_")
        return host_new
    
    @api.multi
    def export_service(self):
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        host = self.get_host_name()
        host_new = self.get_host_name_new()
        
        serv='test'
        base_url = ir_config.get_param("web.base.url")
        if base_url.find('o.nstda.or.th') > 0:
            serv = "pro"
        config_url = ir_config.get_param('nstdaconf_report.url_%s' % serv)
        config_username = ir_config.get_param('nstdaconf_report.jaster_user_%s' % serv)
        config_password = ir_config.get_param('nstdaconf_report.jaster_pass_%s' % serv)
        
        # EXPORT TO PRO ONLY
        config_odoo_url_pro = ir_config.get_param('nstdaconf_report.odoo_url_pro')
        
        j = jasperclient.JasperClient(config_url, config_username, config_password)
        
        ds_uri = '/Datasources/' + config_odoo_url_pro + '/gnc'
        res_uri = '/Reports/' + config_odoo_url_pro + '/gnc'
        user_id = 'jasper_gnc'
        filename = host_new
    
        export = j.export_service(ds_uri, res_uri, user_id, filename)
        if export:
            print("Download %s Success" % (filename))
        else:
            print("Download %s Fail" % (filename))
            
    @api.multi
    def modify_zip(self):
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        host = self.get_host_name()
        host_new = self.get_host_name_new()
        
        serv='test'
        base_url = ir_config.get_param("web.base.url")
        if base_url.find('o.nstda.or.th') > 0:
            serv = "pro"
        config_url = ir_config.get_param('nstdaconf_report.url_%s' % serv)
        config_username = ir_config.get_param('nstdaconf_report.jaster_user_%s' % serv)
        config_password = ir_config.get_param('nstdaconf_report.jaster_pass_%s' % serv)
        
        config_odoo_url_pro = ir_config.get_param('nstdaconf_report.odoo_url_pro')
        
        config_db_url_pro = ir_config.get_param('nstdaconf_report.db_url_pro')
        config_db_port_pro = ir_config.get_param('nstdaconf_report.db_port_pro')
        config_db_name_pro = ir_config.get_param('nstdaconf_report.db_name_pro')
        
        config_db_url_test = ir_config.get_param('nstdaconf_report.db_url_test')
        config_db_port_test = ir_config.get_param('nstdaconf_report.db_port_test')
        config_db_name_test = ir_config.get_param('nstdaconf_report.db_name_test')

        j = jasperclient.JasperClient(config_url, config_username, config_password)
        
        filename = "export_" + host_new + ".zip"
        replace_serv_prd = config_odoo_url_pro
        replace_serv_test = host_new
        
        prd_db_url = config_db_url_pro
        prd_db_port = config_db_port_pro
        prd_db_dbname = config_db_name_pro
        test_db_url = config_db_url_test
        test_db_port = config_db_port_test
        test_db_dbname = config_db_name_test
        
        j.modify_zipfile(filename, replace_serv_prd, replace_serv_test, prd_db_url, prd_db_port, prd_db_dbname, test_db_url, test_db_port, test_db_dbname)
        
    
    @api.multi
    def import_service(self):
        ir_config = self.env['ir.config_parameter']
        base_url = ir_config.get_param("web.base.url")
        host = self.get_host_name()
        host_new = self.get_host_name_new()
        
        # IMPORT TO SERVER TEST ONLY
        serv='test'
        config_url = ir_config.get_param('nstdaconf_report.url_%s' % serv)
        config_username = ir_config.get_param('nstdaconf_report.jaster_user_%s' % serv)
        config_password = ir_config.get_param('nstdaconf_report.jaster_pass_%s' % serv)

        j = jasperclient.JasperClient(config_url, config_username, config_password)
        
        j.import_service(host_new)
        