# -*- coding: utf-8 -*-
from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    res_section_id = fields.Many2one(
        'res.section',
        string='Section',
        help="Default budget used in the order line",
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        help="Default taxbranch used in the order line",
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        help="Default operating unit for this pos order",
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        domain="[('operating_unit_id', '=', operating_unit_id)]",
        help="Default warehouse for this pos order",
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        domain="[('operating_unit_id', '=', operating_unit_id)]",
        help="Default source location for this pos",
    )
    pos_partner_id = fields.Many2one(
        'res.partner',
        string='Default POS Customer',
        required=True,
        domain=[('customer', '=', True)],
        help="If partner is not specified, this will be used as default",
    )
    # More workflow option
    voucher_journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        domain=[('type', 'in', ('bank', 'cash'))],
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Receipt Bank Account',
    )
