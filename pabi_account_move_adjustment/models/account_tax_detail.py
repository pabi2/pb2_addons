# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountTaxDetail(models.Model):
    _inherit = 'account.tax.detail'

    vat = fields.Char(
        string='Tax ID',
        related='partner_id.vat',
        readonly=True,
    )
    taxbranch = fields.Char(
        string='Tax Branch ID',
        related='partner_id.taxbranch',
        readonly=True,
    )

    # @api.multi
    # @api.depends('invoice_tax_id', 'voucher_tax_id')
    # def _compute_taxbranch_id(self):
    #     """ Overwrite """
    #     for rec in self:
    #         if rec.invoice_tax_id:
    #             rec.taxbranch_id = rec.invoice_tax_id.invoice_id.taxbranch_id
    #         elif rec.voucher_tax_id:
    #             rec.taxbranch_id = rec.voucher_tax_id.invoice_id.taxbranch_id
    #         elif rec.ref_move_id:
    #             taxbranches = rec.ref_move_id.line_id.\
    #                 filtered('is_tax_line').mapped('taxbranch_id')
    #             rec.taxbranch_id = taxbranches and taxbranches[0] or False
