# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    force_tax_rounding_method = fields.Selection(
        [('round_per_line', 'Round per line'),
         ('round_globally', 'Round globally')],
        string='Force Tax Rounding',
    )

    @api.multi
    def _amount_all(self, field_name, arg):
        """ Pass context when force_tax_rounding_method is set """
        methods = self.mapped('force_tax_rounding_method')
        if len(methods) > 1:
            raise ValidationError(_('> 1 force rounding method!'))
        if len(methods) == 1:
            self = self.with_context(force_tax_rounding_method=methods[0])
        return super(SaleOrder, self)._amount_all(field_name, arg)

    @api.v7
    def _amount_line_tax(self, cr, uid, line, context=None):
        """ Overwrite, to add context to compute_all() """
        val = 0.0
        line_obj = self.pool['sale.order.line']
        price = line_obj._calc_line_base_price(cr, uid, line, context=context)
        qty = line_obj._calc_line_quantity(cr, uid, line, context=context)
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.tax_id, price, qty, line.product_id,
                line.order_id.partner_id,
                context=context)['taxes']:
            val += c.get('amount', 0.0)
        return val
