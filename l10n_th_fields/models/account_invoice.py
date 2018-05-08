# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        'sale.order',
        'sale_order_invoice_rel', 'invoice_id', 'order_id',
        copy=False,
        string='Sales Orders',
        readonly=True,
        help="This is the list of sale orders linked to this invoice.",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
