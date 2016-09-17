# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    by_fiscalyear = fields.Boolean(
        string='By Fiscal Year',
    )
    
    @api.model
    def _create_invoice_line(self, inv_line_data, inv_lines, po_line):
        installment = self._context.get('installment', False)
        if installment:
            installment = self.env['purchase.invoice.plan'].search([('installment', '=', installment),
                                           ('order_id', '=', po_line.order_id.id),
                                           ('state', 'in', [False, 'cancel'])])
        if installment:
            fiscalyear = installment.fiscal_year_id
            if po_line.order_id.by_fiscalyear:
                if po_line.fiscal_year_id == fiscalyear:
                    inv_line_obj = self.env['account.invoice.line']
                    inv_line_id = inv_line_obj.create(inv_line_data).id
                    inv_lines.append(inv_line_id)
                    po_line.write({'invoice_lines': [(4, inv_line_id)]})
        return inv_lines


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fiscal_year_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    by_fiscalyear = fields.Boolean(
        related='order_id.by_fiscalyear',
        string='By Fiscal Year',
    )


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    fiscal_year_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )