# -*- encoding: utf-8 -*-
from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    run_now = fields.Boolean(
        string='Immediate Run',
        default=False,
        help="Validate picking and invoice as soon as order is confimed."
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        help="Default budget used in the order line",
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        help="Default taxbranch used in the order line",
    )
