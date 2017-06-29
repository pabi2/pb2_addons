# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiSupplierSummarizeReportWizard(models.TransientModel):

    _name = 'pabi.supplier.summarize.report.wizard'

    date_from = fields.Date(string='Contract End Date From')
    date_to = fields.Date(string='Contract End Date To')
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
            'pabi_supplier_summarize_report' or \
            'pabi_supplier_summarize_report_xls'
        # datestring = fields.Date.context_today(self)
        # For SQL, we search simply pass params
        # data['parameters']['date_from'] = self.date_from or 'Null'
        # data['parameters']['date_to'] = self.date_to or 'Null'
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
