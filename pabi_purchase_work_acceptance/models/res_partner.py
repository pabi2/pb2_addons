# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_delivery_penalty_product_id = fields.Many2one(
        'product.product',
        string="Delivery Penalty Product",
        company_dependent=True,
        required=True,
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
