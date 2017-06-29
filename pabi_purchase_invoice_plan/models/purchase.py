# -*- coding: utf-8 -*-
import math

from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    advance_rounding = fields.Boolean(
        string="Advance Rounding",
        readonly=True,
    )

    @api.model
    def _action_invoice_create_hook(self, invoice_ids):
        # For Hook
        res = super(PurchaseOrder, self).\
            _action_invoice_create_hook(invoice_ids)
        if self.use_advance and self.advance_rounding and \
                self.invoice_method == 'invoice_plan':
            adv_invoice = self.env['account.invoice'].\
                search([('id', 'in', invoice_ids), ('is_advance', '=', True)])
            adv_amount = adv_invoice[0].invoice_line[0].price_unit
            invoices = self.env['account.invoice'].\
                search([('id', 'in', invoice_ids), ('is_advance', '=', False)],
                       order='date_invoice')
            if invoices:
                total_invoices = len(invoices.ids)
                adv_accum = 0.0
                count = 1
                for invoice in invoices:
                    if count < total_invoices:
                        for line in invoice.invoice_line:
                            price_subtotal_frac, price_subtotal_whole =\
                                math.modf(line.price_subtotal)
                            if line.price_subtotal < 0:
                                if price_subtotal_frac:  # change
                                    line.price_unit = price_subtotal_whole
                                adv_accum += price_subtotal_whole
                    if count == total_invoices:
                        for line in invoice.invoice_line:
                            if line.price_subtotal < 0:
                                line.price_unit = -(adv_amount + adv_accum)
                    count += 1
        return res

    @api.model
    def _create_invoice_line(self, inv_line_data, inv_lines, po_line):
        if not po_line.order_id.by_fiscalyear:
            return super(PurchaseOrder, self).\
                _create_invoice_line(inv_line_data, inv_lines, po_line)

        installment = self._context.get('installment', False)
        if installment:
            installment = \
                self.env['purchase.invoice.plan'].search(
                    [('installment', '=', installment),
                     ('order_id', '=', po_line.order_id.id),
                     ('state', 'in', [False, 'cancel'])]
                )
        if installment:
            fiscalyear = installment[0].fiscalyear_id
            if po_line.order_id.by_fiscalyear:
                if po_line.fiscalyear_id == fiscalyear:
                    inv_line_obj = self.env['account.invoice.line']
                    inv_line_id = inv_line_obj.create(inv_line_data).id
                    inv_lines.append(inv_line_id)
                    po_line.write({'invoice_lines': [(4, inv_line_id)]})
        return inv_lines


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    by_fiscalyear = fields.Boolean(
        related='order_id.by_fiscalyear',
        string='By Fiscal Year',
    )


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
