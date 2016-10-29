# -*- coding: utf-8 -*-
from openerp import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    has_supplier_retention = fields.Boolean(
        string='Has Supplier Retention',
        compute='_compute_has_supplier_retention',
        help="This purchase has uncleared supplier retention, i.e.,\n"
        " * Contract Warranty (customer invoices)\n"
        " * Retention on Supplier Invoice (invoice plan)\n",
    )

    @api.multi
    @api.depends()
    def _compute_has_supplier_retention(self):
        Invoice = self.env['account.invoice']
        for po in self:
            # 1) Contract Warranty (customer_invoice)
            count = Invoice.search([('partner_id', '=', po.partner_id.id),
                                    ('state', 'in', ['open', 'paid']),
                                    ('retention_purchase_id', '=', po.id)],
                                   count=True)
            if count:
                po.has_supplier_retention = True
                continue
            # 2) Retention from Supplier Invoice (invoice plan)
            count = Invoice.search([('partner_id', '=', po.partner_id.id),
                                    ('amount_retention', '>', 0.0),
                                    ('purchase_ids', 'in', [po.id])],
                                   count=True)
            if count:
                po.has_supplier_retention = True
                continue
            po.has_supplier_retention = False
