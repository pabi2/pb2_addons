# -*- coding: utf-8 -*-
import ast
import logging
from openerp import models, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def action_pr_to_po(self):
        # Requisition created
        req_ids = self.action_pr_to_req()
        _logger.info("Requisition created - %s", req_ids)
        # PO Created
        reqs = self.env['purchase.requisition'].browse(req_ids)
        po_ids = reqs.action_req_to_po()
        _logger.info("PO created - %s", po_ids)
        return po_ids

    @api.multi
    def action_pr_to_req(self):
        req_ids = []
        for pr in self:
            # To Approve it
            if pr.state == 'draft':
                pr.button_to_approve()
                pr.button_approved()
                MakePrq = self.env['purchase.request.line.'
                                   'make.purchase.requisition']
                ctx = {'active_ids': pr.line_ids.ids,
                       'active_model': 'purchase.request.line'}
                make_prq = MakePrq.with_context(ctx).create({})
                res = make_prq.make_purchase_requisition()
                req_ids += ast.literal_eval(res['domain'])[0][2]
        return req_ids


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def action_req_to_po(self):
        purchase_ids = []
        for req in self:
            # To Approve it
            if req.state == 'draft':
                # Select an Asset first in product_id, A7440-001-0001 (PC)
                Product = self.env['product.product']
                code = 'A7440-001-0001'
                product = Product.search([('default_code', '=', code)])
                req.line_ids.write({'product_id': product.id})
                # Confirm
                req.signal_workflow('sent_suppliers')
                # Create 1 RFQ
                RFQCreate = self.env['purchase.requisition.partner']
                ctx = {'active_ids': [req.id], 'active_id': req.id}
                partner_id = self.env['res.partner'].search(
                    [('supplier', '=', True)], limit=1).id
                vals = {'partner_id': partner_id}
                rfq_create = RFQCreate.with_context(ctx).create(vals)
                rfq_create.create_order()
                # Confirm the PO
                req.purchase_ids.signal_workflow('purchase_confirm')
                # Verify this CFB
                req.signal_workflow('to_verify')
                req.signal_workflow('verified')
                for quote in req.purchase_ids:
                    res = quote.action_button_convert_to_order()
                    purchase_ids.append(res['res_id'])
        purchases = self.env['purchase.order'].browse(purchase_ids)
        for purchase in purchases:
            purchase.write({'payment_term_id': 1})  # Immediate
        return purchase_ids


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_po_to_invoice(self):
        if len(self) > 1:
            raise ValidationError(_('Please select only 1 PO'))
        for po in self:
            # To confirm, must start from draft
            if po.state == 'draft':
                po.wkf_validate_invoice_method()
                po.wkf_confirm_order()
            # Release
            if po.state == 'confirmed':
                po.wkf_approve_order()
                if po.has_stockable_product():
                    po.action_picking_create()
                else:
                    po.picking_done()
            # Create WA
            acceptance = False
            if po.state == 'approved':
                ctx = {'active_ids': [po.id]}
                CreateWA = self.env['create.purchase.work.acceptance']
                res = CreateWA.with_context(ctx).default_get([])
                create_wa = CreateWA.create(res)
                acceptance = create_wa.with_context(ctx)._prepare_acceptance()
                acceptance.write({'order_id': po.id})
                # Evaluate
                for line in acceptance.acceptance_line_ids:
                    line.write({'to_receive_qty': line.balance_qty})
            # If PO has IN, then do the transfer and create invoice
            if po.has_stockable_product() and po.picking_ids:
                po.picking_ids.write({'acceptance_id': acceptance.id})
                # Transfer it
                picking = po.picking_ids[0]
                res = picking.do_enter_transfer_details()
                Transfer = self.env['stock.transfer_details']
                transfer = Transfer.browse(res['res_id'])
                res = transfer.do_detailed_transfer()

                # # Create invoice
                # StockInvoice = self.env['stock.invoice.onshipping']
                # ctx = {'active_ids': [picking.id]}
                # stock_invoice = StockInvoice.with_context(ctx).create({})
                # stock_invoice.open_invoice()

            else:  # No IN, create invoice from WA
                WA = self.env['purchase.work.acceptance']
                LineInvoice = self.env['purchase.order.line_invoice']
                res = WA.open_order_line([acceptance.id])
                ctx = {'active_model': 'purchase.work.acceptance',
                       'active_id': acceptance.id}
                res['context'].update(ctx)
                line_inv = LineInvoice.with_context(res['context']).create({})
                line_inv.makeInvoices()

            # # Create Billing
            # Billing = self.env['purchase.billing']
            # billing = Billing.create({'partner_id': po.partner_id.id})
            # billing._onchange_partner_id()
            # billing.supplier_invoice_ids = po.invoice_ids
            # billing.validate_billing()
        return True
