# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('type')
    def _compute_doctype(self):
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   self.type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def _finalize_voucher(self, voucher):
        voucher = super(AccountVoucher, self)._finalize_voucher(voucher)
        if voucher.doctype_id.sequence_id:
            # Get doctype sequence for document number
            sequence_id = voucher.doctype_id.sequence_id.id
            fiscalyear_id = voucher.period_id.fiscalyear_id.id
            voucher.number = self.\
                with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            # Use document number for journal entry
            voucher.move_id.ref = voucher.number
        return voucher
