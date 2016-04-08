# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class account_invoice(models.Model):

    _inherit = "account.invoice"

    is_advance = fields.Boolean(
        string='Advance',
        readonly=True,
    )
    is_deposit = fields.Boolean(
        string='Deposit',
    )
    purchase_ids = fields.Many2many(
        'purchase.order',
        'purchase_invoice_rel', 'invoice_id', 'purchase_id',
        copy=False,
        string='Purchase Orders',
        readonly=True,
        help="This is the list of purchase orders linked to this invoice.",
    )

    @api.multi
    def action_cancel(self):
        """ For Advance (is_advance=True), do not allow cancellation
        any of the following invoices is confirmed"""
        for inv in self:
            # Other invoices exists
            if inv.is_advance or inv.is_deposit:
                for invoice in inv.purchase_ids.invoice_ids:
                    if invoice.state not in ('draft', 'cancel'):
                        raise UserError(
                            _("""Cancellation of advance invoice is not allowed!
                            Please cancel all following invoices first."""))
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
