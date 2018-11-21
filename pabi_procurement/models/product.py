# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_ok = fields.Boolean(
        default=False,
    )
    cost_method = fields.Selection(
        default='average',
    )
    property_account_income_categ = fields.Many2one(
        'account.account',
        related='categ_id.property_account_income_categ',
    )
    property_account_expense_categ = fields.Many2one(
        'account.account',
        related='categ_id.property_account_expense_categ',
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_consumable = fields.Boolean(
        string="Is Consumable",
        default=False,
        help="For service product, but want to calculate fine as consumable."
    )
