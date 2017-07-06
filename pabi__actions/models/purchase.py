# -*- coding: utf-8 -*-
import ast
import logging
from openerp import models, api

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
        return purchase_ids
