# -*- coding: utf-8 -*-
from openerp import models


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'default_code'  # Remove name sorting for performance improve
