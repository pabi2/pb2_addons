# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Selection(
        [('quotation', 'Quotation'),
         ('purchase_order', 'Purchase Order'), ],
        string='Order Type',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('order_type', 'quotation'),
    )
    quote_id = fields.Many2one(
        'purchase.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Order Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    state2 = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Mail Sent'),
         ('cancel', 'Cancelled'),
         ('done', 'Done'), ],
        string='Status',
        readonly=True,
        related='state',
        help="A dummy state used for Quotation",
    )
    invoice_method = fields.Selection(
        [('manual', 'Based on Purchase Order lines'),
         ('order', 'Based on generated draft invoice'),
         ('picking', 'Based on incoming shipments'), ]
    )

    @api.model
    def create(self, vals):
        if (vals.get('order_type', False) or
            self._context.get('order_type', 'quotation')) == 'quotation' \
                and vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get(
                'purchase.quotation') or '/'
        new_order = super(PurchaseOrder, self).create(vals)
        return new_order

    @api.multi
    def action_button_convert_to_order(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        order = self.copy({
            'name': self.env['ir.sequence'].get('purchase.order') or '/',
            'order_type': 'purchase_order',
            'quote_id': self.id,
            'partner_ref': self.partner_ref,
        })
        self.order_id = order.id  # Reference from this quotation to order
        self.signal_workflow('convert_to_order')
        self.state2 = 'done'
        return self.open_purchase_order()

    def open_purchase_order(self):
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'purchase.order',
            'context': {
                'search_default_my_purchase_orders_filter': 1,
                'order_type': 'purchase_order',
                # hide_reports is used to hide forms by its name
                # as we don't want to display sales form in quotation window
                # To be used later !!!
                # 'hide_reports': ['sale.report_saleorder',
                #                  'nstda.msd.quotation'],
            },
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'domain': "[('order_type', '=', 'purchase_order')]",
            'res_id': self.order_id and self.order_id.id or False,
        }
