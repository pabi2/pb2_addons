# -*- coding: utf-8 -*-
from openerp import models
from openerp import SUPERUSER_ID
from openerp.api import Environment


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def init(self, cr):
        # Always auto post every journal
        env = Environment(cr, SUPERUSER_ID, {})
        # Case 1: PO17000137
        purchase = env['purchase.order'].\
            search([('name', '=', 'PO17000137')], limit=1)
        l = 40
        i = 0
        while i < l:
            purchase.copy()
            i += 1
        # Case 2: PO17000168
        purchase = env['purchase.order'].\
            search([('name', '=', 'PO17000168')], limit=1)
        l = 40
        i = 0
        while i < l:
            purchase.copy()
            i += 1
        # Case 3: PO17000169 -> CIV17000006
        purchase = env['purchase.order'].\
            search([('name', '=', 'PO17000169')], limit=1)
        invoice = env['account.invoice'].\
            search([('number', '=', 'CIV17000006')], limit=1)
        l = 40
        i = 0
        while i < l:
            new_purchase = purchase.copy()
            new_invoice = invoice.copy()
            new_invoice.retention_purchase_id = new_purchase
            i += 1
        # Case 4: PO17000171
        purchase = env['purchase.order'].\
            search([('name', '=', 'PO17000171')], limit=1)
        l = 40
        i = 0
        while i < l:
            purchase.copy()
            i += 1
