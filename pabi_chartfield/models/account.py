# -*- coding: utf-8 -*-
from openerp import models, api, fields
from .chartfield import ChartFieldAction


class AccountModelLine(ChartFieldAction, models.Model):
    _inherit = 'account.model.line'

    # This field may not be used, but we need it as refereto ChartFieldAction
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    @api.model
    def create(self, vals):
        res = super(AccountModelLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
