# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiStandardAssetReportWizard(models.TransientModel, Common):

    _name = 'pabi.standard.asset.report.wizard'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
    )
    is_standard = fields.Selection(
        [
            ('all', 'All'),
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        string='Standard',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    partner_tag_ids = fields.Many2many(
        'res.partner.tag',
        string='Supplier Type',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )

    @api.multi
    def xls_export(self):
        fields = [
            'org_ids',
            'method_id',
            'is_standard',
            'partner_id',
            'order_id',
            'date_from',
            'date_to',
        ]
        report_name = 'xlsx_report_pabi_standard_asset'
        return self._get_report(fields, report_name)
