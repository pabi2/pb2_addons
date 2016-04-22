# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartField, HeaderTaxBranch


class PurchaseRequisition(HeaderTaxBranch, models.Model):
    _inherit = 'purchase.requisition'

    taxbranch_id = fields.Many2one(
        compute='_compute_taxbranch_id',
        store=True,
    )

    @api.one
    @api.depends('line_ids')
    def _compute_taxbranch_id(self):
        lines = self.line_ids
        self.taxbranch_id = self._check_taxbranch_id(lines)


class PurchaseRequisitionLine(ChartField, models.Model):
    _inherit = 'purchase.requisition.line'
