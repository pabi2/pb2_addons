# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiMonthlyWorkAcceptanceReportWizard(models.TransientModel):

    _name = 'pabi.monthly.work.acceptance.report.wizard'

    operating_unit = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    month = fields.Many2one(
        'account.period',
        string='Month',
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
            'pabi_monthly_work_acceptance_report' or \
            'pabi_monthly_work_acceptance_report_xls'
        # For SQL, we search simply pass params
        data['parameters']['operating_unit'] = self.operating_unit.id
        data['parameters']['month'] = self.month.id
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
