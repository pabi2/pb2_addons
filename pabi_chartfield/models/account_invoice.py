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
    # OVERWRITE
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        domain=[],
        # domain="[('id', 'in', taxbranch_ids and "
        # "taxbranch_ids[0] and taxbranch_ids[0][2] or False)]",
        help="For inovice only, allow accountant to choose taxbranch at will",
    )
    taxbranch_mismatch = fields.Boolean(
        compute='_compute_taxbranch_ids',
    )

    def _set_header_taxbranch_id(self):
        """ Overwrite, do not set tax branch, user must choose at will """
        if not self.taxbranch_id and len(self.taxbranch_ids) == 1:
            self.taxbranch_id = self.taxbranch_ids[0]
    # -- OVERWRITE

    @api.one
    @api.depends('invoice_line')
    def _compute_taxbranch_ids(self):
        lines = self.invoice_line
        self._set_taxbranch_ids(lines)
        # OVERWRITE
        if self.len_taxbranch and self.taxbranch_id not in self.taxbranch_ids:
            self.taxbranch_mismatch = True
        # -- OVERWRITE

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
