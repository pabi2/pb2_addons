# -*- coding: utf-8 -*-

from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    retention_purchase_id = fields.Many2one(
        'purchase.order',
        string='Retention on Purchase',
        domain="[('partner_id', '=', partner_id),"
        "('order_type', '=', 'purchase_order'),"
        "('state', 'in', ['done', 'approved'])]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Visible in Customer Invoice only, to create retention invoice",
    )
    is_retention_return = fields.Boolean(
        string='Return Retention on PO',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    retention_return_purchase_id = fields.Many2one(
        'purchase.order',
        string='Return Retention on Purchase',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Visible in Supplier Invoice only, to create return retention "
        "consisting of amount from retention invoice, and invoice plan",
    )

    @api.multi
    def onchange_partner_id(self, ttype, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            ttype, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if not res:
            res = {}
        if 'value' not in res:
            res['value'] = {}
        res['value'].update({'retention_purchase_id': False,
                             'retention_return_purchase_id': False})
        return res

    @api.onchange('retention_purchase_id')
    def _onchange_retention_purchase_id(self):
        self.invoice_line = False
        if self.retention_purchase_id:
            retention_line = self.env['account.invoice.line'].new()
            retention_line.account_id = \
                self.env.user.company_id.account_retention_supplier
            retention_line.name = \
                self.env.user.company_id.account_retention_supplier.name
            retention_line.quantity = 1.0
            self.invoice_line += retention_line

    @api.onchange('retention_return_purchase_id')
    def _onchange_retention_return_purchase_id(self):
        self.invoice_line = False
        if self.retention_return_purchase_id:
            account_retention_supplier = \
                self.env.user.company_id.account_retention_supplier
            purchase = self.retention_return_purchase_id
            # 1) Customer Invoice Retention
            retention_invoices = self.search(
                [('retention_purchase_id', '=', purchase.id),
                 ('state', 'in', ['open', 'paid'])])
            for inv in retention_invoices:
                for line in inv.invoice_line:
                    if line.account_id != account_retention_supplier:
                        continue
                    return_line = self.env['account.invoice.line'].new()
                    return_line.account_id = account_retention_supplier
                    return_line.name = account_retention_supplier.name + \
                        ' (%s)' % (inv.number,)
                    return_line.quantity = line.quantity
                    return_line.price_unit = line.price_unit
                    self.invoice_line += return_line
            # 2) Customer Invoice Retention
            invoices = purchase.invoice_ids.filtered(
                lambda l: l.amount_retention and l.state in ['open', 'paid'])
            for inv in invoices:
                return_line = self.env['account.invoice.line'].new()
                return_line.account_id = account_retention_supplier
                return_line.name = account_retention_supplier.name + \
                    ' (%s)' % (inv.number,)
                return_line.quantity = 1.0
                return_line.price_unit = inv.amount_retention
                self.invoice_line += return_line
