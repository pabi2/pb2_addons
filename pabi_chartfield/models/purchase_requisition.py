# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class PurchaseRequisition(HeaderTaxBranch, models.Model):
    _inherit = 'purchase.requisition'

    taxbranch_ids = fields.Many2many(
        compute='_compute_taxbranch_ids',
    )
    len_taxbranch = fields.Integer(
        compute='_compute_taxbranch_ids',
    )

    @api.one
    @api.depends('line_ids')
    def _compute_taxbranch_ids(self):
        lines = self.line_ids
        self._set_taxbranch_ids(lines)

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisition, self).create(vals)
        res._set_header_taxbranch_id()
        return res


class PurchaseRequisitionLine(ChartFieldAction, models.Model):
    _inherit = 'purchase.requisition.line'

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisitionLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
