# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class PurchaseOrder(HeaderTaxBranch, models.Model):
    _inherit = 'purchase.order'

    taxbranch_ids = fields.Many2many(
        compute='_compute_taxbranch_ids',
    )
    len_taxbranch = fields.Integer(
        compute='_compute_taxbranch_ids',
    )

    @api.one
    @api.depends('order_line')
    def _compute_taxbranch_ids(self):
        lines = self.order_line
        self._set_taxbranch_ids(lines)

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        res._set_header_taxbranch_id()
        return res


class PurchaseOrderLine(ChartFieldAction, models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
