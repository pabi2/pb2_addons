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
    def _compute_has_supplier_retention(self):
        Invoice = self.env['account.invoice']
        for po in self:
            # 1) Contract Warranty (customer_invoice)
            count = len(Invoice.search(
                [('partner_id', '=', po.partner_id.id),
                 ('state', 'in', ['open', 'paid']),
                 ('retention_purchase_id', '=', po.id)])._ids)
            if count:
                po.has_supplier_retention = True
                continue
            # 2) Retention from Supplier Invoice (invoice plan)
            count = len(Invoice.search(
                [('partner_id', '=', po.partner_id.id),
                 ('amount_retention', '>', 0.0),
                 ('purchase_ids', 'in', [po.id])])._ids)
            if count:
                po.has_supplier_retention = True
                continue
            po.has_supplier_retention = False

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        partner_id = \
            self._context.get('retention_return_to_supplier_id', False)
        if 'retention_return_to_supplier_id' in self._context and \
                not partner_id:
            args += [('id', 'in', [])]
        elif partner_id:
            domain = []
            Invoice = self.env['account.invoice']
            inv_dom = [('partner_id', '=', partner_id),
                       ('state', 'in', ['open', 'paid'])]
            # Exclude PO already used by a valid supplier invoice
            invoices = Invoice.search(
                inv_dom + [('type', 'in', ['in_invoice', 'in_refund']),
                           ('is_retention_return', '=', True)])
            ex_po_ids = invoices.mapped('retention_return_purchase_id').ids
            domain.append(('id', 'not in', ex_po_ids))
            # Includes
            # 1) Contract Warranty (customer_invoice)
            invoices = Invoice.search(
                inv_dom + [('type', 'in', ['out_invoice', 'out_refund']),
                           ('retention_purchase_id', '!=', False)])
            po_ids = invoices.mapped('retention_purchase_id').ids
            # 2) Retention from Supplier Invoice (invoice plan)
            invoices = Invoice.search(
                inv_dom + [('type', 'in', ['in_invoice', 'in_refund']),
                           ('amount_retention', '>', 0.0)])
            for invoice in invoices:
                if invoice.purchase_ids:
                    po_ids += invoice.purchase_ids._ids
            domain.append(('id', 'in', po_ids))
            args += domain
        return super(PurchaseOrder, self).name_search(name=name,
                                                      args=args,
                                                      operator=operator,
                                                      limit=limit)
