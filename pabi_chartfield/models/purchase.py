# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class PurchaseOrder(HeaderTaxBranch, models.Model):
    _inherit = 'purchase.order'

    taxbranch_id = fields.Many2one(
        compute='_compute_taxbranch_id',
        store=True,
    )

    @api.one
    @api.depends('order_line')
    def _compute_taxbranch_id(self):
        lines = self.order_line
        self.taxbranch_id = self._check_taxbranch_id(lines)


class PurchaseOrderLine(ChartFieldAction, models.Model):
    _inherit = 'purchase.order.line'
