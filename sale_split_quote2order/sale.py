# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class sale_order(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        [('quotation', 'Quotation'),
         ('sale_order', 'Sales Order'), ],
        string='Order Type',
        readonly=True,
        index=True,
        default=lambda self: self._context.get('order_type', 'sale_order'),
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quotation Reference',
        readonly=True,
        ondelete='restrict',
        copy=False,
    )
    order_id = fields.Many2one(
        'sale.order',
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

    @api.model
    def create(self, vals):
        if (vals.get('order_type', False) or
            self._context.get('order_type', False)) == 'quotation' \
                and vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('sale.quotation') or '/'
        new_order = super(sale_order, self).create(vals)
        return new_order

    @api.multi
    def action_button_convert_to_order(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        order = self.copy({
            'name': self.env['ir.sequence'].get('sale.order') or '/',
            'order_type': 'sale_order',
            'quote_id': self.id,
            'client_order_ref': self.client_order_ref,
        })
        self.order_id = order.id  # Reference from this quotation to order
        self.signal_workflow('convert_to_order')
        return self.open_sale_order()

    def open_sale_order(self):
        return {
            'name': _('Sales Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'sale.order',
            'context': {
                'search_default_my_sale_orders_filter': 1,
                'order_type': 'sale_order',
                # hide_reports is used to hide forms by its name
                # as we don't want to display sales form in quotation window
                # To be used later !!!
                'hide_reports': ['sale.report_saleorder',
                                 'nstda.msd.quotation'],
            },
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': "[('order_type', '=', 'sale_order')]",
            'res_id': self.order_id and self.order_id.id or False,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
