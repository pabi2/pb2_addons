# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ReportSamplePartnerSQLWizard(models.TransientModel):

    _name = 'report.sample.partner.sql.wizard'

    customer = fields.Boolean(
        string='Customer',
        default=True,
    )
    supplier = fields.Boolean(
        string='Supplier',
        default=True,
    )
    format = fields.Selection(
        [('pdf', 'PDF'),
         ('xls', 'Excel')],
        string='Format',
        required=True,
        default='pdf',
    )

    @api.multi
    def run_report(self):
        data = {'parameters': {}}
        report_name = self.format == 'pdf' and 'report_sample_partner_sql' or \
            'report_sample_partner_sql_xls'
        # For SQL, we search simply pass params
        data['parameters']['customer'] = self.customer
        data['parameters']['supplier'] = self.supplier
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
