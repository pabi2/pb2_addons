# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    investment_id = fields.Many2one(
        'res.partner.investment',
        string='Investment',
        index=True,
        ondelete='restrict',
        readonly=True,
    )
    ref_payments = fields.Char(
        string='Ref Payments',
        compute='_compute_ref_payments',
    )

    @api.multi
    def _compute_ref_payments(self):
        for rec in self:
            ref_payments = rec.invoice.payment_ids.mapped('ref')
            rec.ref_payments = ', '.join(ref_payments)
