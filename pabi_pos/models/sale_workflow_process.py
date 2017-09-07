# -*- encoding: utf-8 -*-
from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    run_now = fields.Boolean(
        string='Immediate Run',
        default=False,
        help="Validate picking and invoice as soon as order is confimed."
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        help="Default budget used in the order line",
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        help="Default taxbranch used in the order line",
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        help="Default warehouse for this pos order",
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        help="Default operating unit for this pos order",
    )
