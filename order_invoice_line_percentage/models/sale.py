# -*- coding: utf-8 -*-

from openerp import models, fields, api


class sale_order(models.Model):

    _inherit = 'sale.order'

    price_include = fields.Boolean(
        string='Tax Included in Price',
        readonly=True,
        compute="_price_include")

    @api.one
    @api.depends('order_line.tax_id')
    def _price_include(self):
        self.price_include = self.order_line and \
            self.order_line[0].tax_id and \
            self.order_line[0].tax_id[0].price_include or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
