# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiStockCardForAccountingReportWizard(models.TransientModel, Common):

    _name = 'pabi.stock.card.for.accounting.report.wizard'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    category_id = fields.Many2one(
        'product.category',
        string='Category',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
    )

    @api.multi
    def xls_export(self):
        fields = [
            'operating_unit_id',
            'product_id',
            'category_id',
            'location_id',
            'date_from',
            'date_to',
        ]
        report_name = 'xlsx_report_pabi_stock_card_for_accounting'
        return self._get_report(fields, report_name)
