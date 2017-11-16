# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    origin_invoice_id = fields.Many2one(
        'account.invoice',
        string='Origin invoice',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    refunded_amount = fields.Float(
        string='Refunded Amount',
        compute='_compute_refunded_amount',
        digits_compute=dp.get_precision('Product Price'),
    )
    refund_invoice_ids = fields.One2many(
        'account.invoice',
        'origin_invoice_id',
        string='Refund Documents',
        domain=[('type', 'in', ('out_refund', 'in_refund'))],
        readonly=True,
        copy=False,
    )

    @api.multi
    @api.depends('refund_invoice_ids.amount_untaxed')
    def _compute_refunded_amount(self):
        for record in self:
            record.refunded_amount = sum(record.refund_invoice_ids.filtered(
                lambda l: l.state != 'cancel').mapped('amount_untaxed'))

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        res = super(AccountInvoice, self).\
            _prepare_refund(invoice, date=date, period_id=period_id,
                            description=description, journal_id=journal_id)
        res.update(origin_invoice_id=invoice.id)
        return res
