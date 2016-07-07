# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class AccountInvoice(HeaderTaxBranch, models.Model):
    _inherit = 'account.invoice'

    taxbranch_id = fields.Many2one(
        compute='_compute_taxbranch_id',
        store=True,
    )

    @api.one
    @api.depends('invoice_line')
    def _compute_taxbranch_id(self):
        lines = self.invoice_line
        self.taxbranch_id = self._check_taxbranch_id(lines)


class AccountInvoiceLine(ChartFieldAction, models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        res = super(AccountInvoiceLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
