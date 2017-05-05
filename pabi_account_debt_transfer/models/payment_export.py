# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PaymentExportLine(models.Model):
    _inherit = 'payment.export.line'

    partner_id = fields.Many2one(
        related=False,
        compute='_compute_partner_id',
    )

    @api.multi
    @api.depends('voucher_id')
    def _compute_partner_id(self):
        for rec in self:
            voucher = rec.voucher_id
            rec.partner_id = voucher.is_transdebt and \
                voucher.transdebt_partner_id or voucher.partner_id
