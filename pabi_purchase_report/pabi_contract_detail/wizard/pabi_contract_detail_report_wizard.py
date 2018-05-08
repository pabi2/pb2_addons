# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiContractDetailReportWizard(models.TransientModel):

    _name = 'pabi.contract.detail.report.wizard'

    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Purchase Type',
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
    )
    date_from = fields.Date(string='Contract Start Date')
    date_to = fields.Date(string='Contract End Date')
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
            'pabi_contract_detail_report' or \
            'pabi_contract_detail_report_xls'
        # datestring = fields.Date.context_today(self)
        # For SQL, we search simply pass params
        data['parameters']['purchase_type'] = self.purchase_type_id.id or 0
        data['parameters']['purchase_method'] = self.purchase_method_id.id or 0
        data['parameters']['date_from'] = self.date_from or 'Null'
        data['parameters']['date_to'] = self.date_to or 'Null'
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
