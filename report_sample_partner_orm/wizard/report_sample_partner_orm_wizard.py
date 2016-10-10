# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ReportSamplePartnerORMWizard(models.TransientModel):

    _name = 'report.sample.partner.orm.wizard'

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
        report_name = self.format == 'pdf' and 'report_sample_partner_orm' or \
            'report_sample_partner_orm_xls'
        # For ORM, we search for ids, and only pass ids to parser and jasper
        Report = self.env['report.sample.partner.orm']
        ids = Report.search(['|', ('customer', '=', self.customer),
                            ('supplier', '=', self.supplier)])._ids
        data['parameters']['ids'] = ids
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
