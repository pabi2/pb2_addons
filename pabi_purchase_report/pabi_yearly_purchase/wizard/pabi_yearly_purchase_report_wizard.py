# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiYearlyPurchaseReportWizard(models.TransientModel):

    _name = 'pabi.yearly.purchase.report.wizard'

    year = fields.Many2one(
        'account.fiscalyear',
        string='Year',
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
        report_name = self.format == 'pdf' and \
            'pabi_yearly_purchase_report' or \
            'pabi_yearly_purchase_report_xls'
        # For SQL, we search simply pass params
        data['parameters']['year'] = self.year.id
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
