# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountTaxDetail(models.Model):
    _inherit = 'account.tax.detail'

    number_preprint = fields.Char(
        string='Preprinted Number',
        compute='_compute_number_preprint',
        store=True,
    )

    @api.multi
    @api.depends('invoice_tax_id', 'voucher_tax_id', 'move_line_id',
                 'invoice_tax_id.invoice_id.number_preprint',
                 'voucher_tax_id.voucher_id.number_preprint',
                 'move_line_id.move_id.ref',)
    def _compute_number_preprint(self):
        for rec in self:
            number_preprint = False
            if rec.invoice_tax_id:
                number_preprint = rec.invoice_tax_id.invoice_id.number_preprint
            elif rec.voucher_tax_id:
                number_preprint = rec.voucher_tax_id.voucher_id.number_preprint
            elif rec.move_line_id:  # For interface documents
                number_preprint = rec.move_line_id.move_id.ref
            rec.number_preprint = number_preprint
