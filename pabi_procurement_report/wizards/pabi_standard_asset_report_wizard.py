# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiStandardAssetReportWizard(models.TransientModel, Common):

    _name = 'pabi.standard.asset.report.wizard'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
    )
    price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Purchase Price Range',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')

    @api.multi
    def xls_export(self):
        fields = [
            'operating_unit_id',
            'method_id',
            'price_range_id',
            'partner_id',
            'order_id',
            'date_from',
            'date_to',
        ]
        report_name = 'xlsx_report_pabi_standard_asset'
        return self._get_report(fields, report_name)
