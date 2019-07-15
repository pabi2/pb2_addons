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
            # 'name': self.env['ir.sequence'].get('purchase.order') or '/',
            'name': '/',  # As we will use doctype order
            'order_type': 'purchase_order',
            'quote_id': self.id,
            'partner_ref': self.partner_ref,
            'order_line': False,
        })
        # assign purchase related id to line
        for quo_line in self.order_line:
            so_line = quo_line.copy()
            so_line.order_id = order.id
            so_line.quo_line_id = quo_line.id
            quo_line.pur_line_id = so_line.id
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
        
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    quo_line_id = fields.Many2one(
        'purchase.order.line',
        string='Quotation Line Reference',
        readonly=True,
        ondelete='restrict',
    )
    pur_line_id = fields.Many2one(
        'purchase.order.line',
        string='Order Line Reference',
        readonly=True,
        ondelete='set null',
    )
               
    def _default_fiscalyear_id(self, cr, uid, context=None):
        a=context
        print str(a)
        order_line_obj = self.pool['purchase.order.line']
        if context.get('order_line'):
            order_line = order_line_obj.browse(cr, uid, context['order_line'][0][1])
        #product=self.search([('', '=', 'value' )]).field2
        return order_line.fiscalyear_id.id
    
    def _default_activity_group_id(self, cr, uid, context=None):
        a=context
        print str(a)
        order_line_obj = self.pool['purchase.order.line']
        if context.get('order_line'):
            order_line = order_line_obj.browse(cr, uid, context['order_line'][0][1])
        #product=self.search([('', '=', 'value' )]).field2
        return order_line.activity_group_id.id
    
    def _default_fund_id(self, cr, uid, context=None):
        a=context
        print str(a)
        order_line_obj = self.pool['purchase.order.line']
        if context.get('order_line'):
            order_line = order_line_obj.browse(cr, uid, context['order_line'][0][1])
        #product=self.search([('', '=', 'value' )]).field2
        return order_line.fund_id.id
    
    
    #product_id = fields.Many2one('product.product', 'Product', domain=[('purchase_ok','=',True)], change_default=True,default=_default_product)
    
    _defaults = {
        'fiscalyear_id' : _default_fiscalyear_id,
        'activity_group_id': _default_activity_group_id,
        'fund_id' : _default_fund_id
        #'costcenter_id': _get_default_cost _default_fund_idcenter_id,
        #'org_id': _get_default_org_id,
    }