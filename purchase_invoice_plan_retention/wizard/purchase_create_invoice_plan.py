# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'

    use_retention = fields.Boolean(
        string='Retention',
        default=False,
    )
    percent_retention = fields.Float(
        string='Percent',
    )
    fixed_retention = fields.Float(
        string='Fixed Amount',
    )
    retention_type = fields.Selection(
        [('before_vat', 'Before VAT (%)'),
         ('after_vat', 'After VAT (%)'),
         ('fixed', 'Fixed Amount')],
        string='Type',
    )

    @api.model
    def _check_retention_account(self):
        prop = self.env.user.company_id.account_retention_supplier
        prop_id = prop and prop.id or False
        account_id = self.env['account.fiscal.position'].map_account(prop_id)
        if not account_id:
            raise UserError(
                _('There is no retention customer account defined.')
            )

    @api.multi
    def do_create_purchase_invoice_plan(self):
        self.ensure_one()
        super(PurchaseCreateInvoicePlan,
              self).do_create_purchase_invoice_plan()
        order = self.env['purchase.order'].browse(self._context['active_id'])
        order.write({'use_retention': self.use_retention,
                     'percent_retention': self.percent_retention,
                     'fixed_retention': self.fixed_retention,
                     'retention_type': self.retention_type})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
