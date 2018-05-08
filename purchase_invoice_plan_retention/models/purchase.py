# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    use_retention = fields.Boolean(
        string='Retention',
        readonly=True,
    )
    percent_retention = fields.Float(
        string='Percent',
        readonly=True,
    )
    fixed_retention = fields.Float(
        string='Fixed Amount',
        readonly=True,
    )
    retention_type = fields.Selection(
        [('before_vat', 'Before VAT (%)'),
         ('after_vat', 'After VAT (%)'),
         ('fixed', 'Fixed Amount')],
        string='Type',
        readonly=True,
    )

    @api.model
    def _prepare_invoice(self, order, lines):
        invoice_vals = \
            super(PurchaseOrder, self)._prepare_invoice(order, lines)
        installment = self._context.get('installment', False)
        if order.use_retention and installment:
            invoice_vals.update({'percent_retention': order.percent_retention,
                                 'fixed_retention': order.fixed_retention,
                                 'retention_type': order.retention_type})
        return invoice_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
