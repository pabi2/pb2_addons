# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class XLSXReportExtendTheRepayment(models.TransientModel):
    _name = 'xlsx.report.extend.the.repayment'
    _inherit = 'xlsx.report'
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner ID',
        )    

    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='For Period',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
          
#     results = fields.Many2many(
#         string='Results',
#         compute='_compute_results',
#         help="Use compute fields, so there is nothing store in database",
#     )
#      
#     @api.model
#     def _domain_to_where_str(self, domain):
#         """ Helper Function for better performance """
#         where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
#                      and "'%s'" % x[2] or x[2]) for x in domain]
#         
#         where_str = 'and'.join(where_dom)
#         where_str = where_str.replace(',)',')')
#         return where_str
     
#     @api.multi
#     def _compute_results(self):
#         """
#         Solution
#         1. Get from account bank receipt
#         2. Check state is done
#         """
#         self.check_date()
#         self.ensure_one()
#         Result = self.env['issi.report.cgd.monthly.view']
#         dom = []
#         if self.partner_id:
#             dom += [('partner_id', '=', self.partner_id.id)]
#         if self.calendar_period_id.date_start:
#             dom += [('date_start','>=',self.calendar_period_id.date_start)]
#         if self.calendar_period_id.date_end:
#             dom += [('date_end','<=',self.calendar_period_id.date_end)]                
#         if dom ==[]:
#             raise ValidationError('Please fill in information')
#         where_str = self._domain_to_where_str(dom) 
#         self._cr.execute("""
#             select row_number() over (order by source_document, invoice_date ) as id, *
#             from issi_report_cgd_monthly 
#             where %s          
#             """% (where_str))
#          
#         sla_receipt = self._cr.dictfetchall()
         
#         for line in sla_receipt:
#             self.results += Result.new(line)