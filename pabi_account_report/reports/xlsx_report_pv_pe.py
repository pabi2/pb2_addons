# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta


class XLSXReportPVPE(models.TransientModel):
    _name = 'xlsx.report.pv.pe'
    _inherit = 'xlsx.report'
    
    date_start = fields.Date(
        string='Start Date',
        default = lambda self: date.today() + relativedelta(day=1,months=-3), 
    )
    
    date_end = fields.Date(
        string='End Date',
        default = fields.Date.today,
    )
   
    results = fields.Many2many(
        'issi.figl.pv.pe.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
            
    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        
        where_str = 'and'.join(where_dom)
        where_str = where_str.replace(',)',')')
        return where_str
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        result = self.env['issi.figl.pv.pe.view']
        dom = [('state','=','done')]
        if self.date_start:
            dom += [('pv_posting_date', '>=', self.date_start)]
        if self.date_end:
            dom += [('pv_posting_date', '<=', self.date_end)]
        where_str = self._domain_to_where_str(dom) 
        self._cr.execute(""" select *
            from issi_figl_pv_pe
            where %s"""% (where_str))
        sla_receipt = self._cr.dictfetchall()

        for line in sla_receipt:
            self.results += result.new(line) 
            
class ISSIFiglPVPE(models.AbstractModel):
    _name = 'issi.figl.pv.pe.view'
    
    journal_id = fields.Integer(
        srting = 'Journal ID',
        )
    gl = fields.Char(
        string = 'GL',
        )
    pe_doc = fields.Char(
        string = 'PE Doc',
        )
    pe_valuedate = fields.Date(
        string = 'PE Value Date',
        )
    pe_transfertype = fields.Char(
        string = 'PE Transfer Type',
        )
    pe_amount = fields.Float(
        string = 'PE Amount',
        )
    pv_doc = fields.Char(
        string = 'PV Doc',
        )
    pv_posting_date = fields.Date(
        string = 'PV Posting Date',
        )
    pv_cheque_date = fields.Date(
        string = 'PV Cheque Date',
        )
    pv_valuedate = fields.Date(
        string = 'PV Value Date',
        )
    pv_amount = fields.Float(
        string = 'PV Amount',
        )
    state = fields.Char(
        string = 'State',
        )
#   