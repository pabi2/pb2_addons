# -*- coding: utf-8 -*-
from ast import literal_eval
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare


class PurchaseLineInvoice(models.TransientModel):
    _inherit = 'purchase.order.line_invoice'

    @api.model
    def default_get(self, fields):
        if self._context['active_model'] == 'purchase.work.acceptance':
            active_id = self._context['active_id']
            WAcceptance = self.env['purchase.work.acceptance']
            lines = []
            acceptance = WAcceptance.browse(active_id)
            for wa_line in acceptance.acceptance_line_ids:
                po_line = wa_line.line_id
                max_quantity = po_line.product_qty - \
                    po_line.invoiced_qty - po_line.cancelled_qty
                if po_line.order_id.invoice_method == 'invoice_plan':
                    max_quantity = po_line.product_qty
                lines.append({
                    'po_line_id': po_line.id,
                    'product_qty': max_quantity,
                    'invoiced_qty': wa_line.to_receive_qty,
                    'price_unit': wa_line.price_unit,
                    'wa_line_qty': wa_line.to_receive_qty,
                })
            defaults = super(PurchaseLineInvoice, self).default_get(fields)
            defaults['line_ids'] = lines
        else:
            defaults = super(PurchaseLineInvoice, self).default_get(fields)
        return defaults

    @api.multi
    def makeInvoices(self):
        self.ensure_one()
        if self._context['active_model'] == 'purchase.work.acceptance':
            # Validate qty > 0 and <= wa_line_qty
            for line in self.line_ids:
                if not line.invoiced_qty:
                    raise ValidationError(
                        _("Quantity to invoice can't be zero!"))
                if float_compare(line.invoiced_qty, line.wa_line_qty, 2) == 1:
                    raise ValidationError(_("Can't receive product's quantity "
                                            "over work acceptance's quantity"))
        # Call super
        res = super(PurchaseLineInvoice, self).makeInvoices()
        if self._context['active_model'] == 'purchase.work.acceptance':
            # Newly created invoice
            invoice_dom = literal_eval(res.get('domain', 'False'))
            invoice_ids = invoice_dom and invoice_dom[0][2] or []
            # WA
            active_id = self._context['active_id']
            WAcceptance = self.env['purchase.work.acceptance']
            acceptance = WAcceptance.browse(active_id)
            acceptance.invoice_created = \
                invoice_ids and invoice_ids[0] or False
            if invoice_ids and acceptance.supplier_invoice:
                invoices = self.env['account.invoice'].browse(invoice_ids)
                invoices.write({'supplier_invoice_number':
                                acceptance.supplier_invoice})
                invoices.button_reset_taxes()
        return res

# Can't receive product's quantity over work acceptance's quantity


class PurchaseLineInvoiceLine(models.TransientModel):
    _inherit = 'purchase.order.line_invoice.line'

    wa_line_qty = fields.Float(
        string='WA Line Quantity',
    )
