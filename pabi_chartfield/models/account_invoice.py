# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .chartfield import ChartFieldAction, HeaderTaxBranch


class AccountInvoice(HeaderTaxBranch, models.Model):
    _inherit = 'account.invoice'

    taxbranch_ids = fields.Many2many(
        compute='_compute_taxbranch_ids',
    )
    len_taxbranch = fields.Integer(
        compute='_compute_taxbranch_ids',
    )

    @api.one
    @api.depends('invoice_line')
    def _compute_taxbranch_ids(self):
        lines = self.invoice_line
        self._set_taxbranch_ids(lines)

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        res._set_header_taxbranch_id()
        return res


class AccountInvoiceLine(ChartFieldAction, models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        res = super(AccountInvoiceLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
