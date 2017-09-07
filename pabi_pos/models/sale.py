# -*- encoding: utf-8 -*-
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, field_list):
        res = super(SaleOrder, self).default_get(field_list)
        process_id = self._context.get('default_workflow_process_id', False)
        if process_id:
            process = self.env['sale.workflow.process'].browse(process_id)
            res['taxbranch_id'] = process.taxbranch_id.id
        return res

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        for order in self.filtered('workflow_process_id'):
            pickings = order.picking_ids.\
                filtered('workflow_process_id.validate_picking')
            pickings.validate_picking()
        return res

    @api.multi
    def action_invoice_create(self):
        res = super(SaleOrder, self).action_invoice_create()
        invoices = self.env['account.invoice'].browse(res)
        for invoice in invoices:
            if invoice.workflow_process_id.validate_invoice:
                invoice.signal_workflow('invoice_open')
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, field_list):
        res = super(SaleOrderLine, self).default_get(field_list)
        process_id = self._context.get('workflow_process_id', False)
        if process_id:
            process = self.env['sale.workflow.process'].browse(process_id)
            res['section_id'] = process.section_id.id
        return res
