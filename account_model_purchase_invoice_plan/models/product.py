# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_fin_lease = fields.Boolean(
        string='Financial Lease',
        default=False,
        help='This will be used in purchase.order to compute is_fin_lease',
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_fin_lease = fields.Boolean(
        string='Financial Lease',
        related='categ_id.is_fin_lease',
        store=True,
        readonly=True,
        help='This will be used in purchase.order to compute is_fin_lease',
    )
