# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PabiStockCardForAccountingReportWizard(models.TransientModel):
    _name = 'pabi.stock.card.for.accounting.report.wizard'

    operating_unit = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    product = fields.Many2one(
        'product.product',
        string='Product',
    )
    category = fields.Many2one(
        'product.category',
        string='Category',
    )
    date_from = fields.Date(
        string='Contract Start Date',
    )
    date_to = fields.Date(
        string='Contract End Date',
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
            'pabi_stock_card_for_accouting_report' or \
            'pabi_stock_card_for_accouting_report_xls'
        # For SQL, we search simply pass params
        data['parameters']['operating_unit'] = self.operating_unit.id
        data['parameters']['product'] = self.product.id
        data['parameters']['category'] = self.category.id
        data['parameters']['date_from'] = self.date_from
        data['parameters']['date_to'] = self.date_to
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
        }
        return res
