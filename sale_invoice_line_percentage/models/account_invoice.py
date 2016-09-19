# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class account_invoice(models.Model):

    _inherit = "account.invoice"

    is_advance = fields.Boolean(
        string='Advance',
        readonly=True)
    sale_ids = fields.Many2many(
        'sale.order',
        'sale_order_invoice_rel', 'invoice_id', 'order_id',
        copy=False,
        string='Sales Orders',
        readonly=True,
        help="This is the list of sale orders linked to this invoice.",
    )

    @api.multi
    def action_cancel(self):
        """ For Advance (is_advance=True), do not allow cancellation
        if advance amount has been deducted on following invoices"""
        for inv in self:
            # Other invoices exists
            if inv.is_advance and inv.sale_ids.invoiced_rate:
                raise except_orm(
                    _('Warning!'),
                    _("""Cancellation of advance invoice is not allowed!
                    Please cancel all following invoices first."""))
        res = super(account_invoice, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
