# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Asset Sequence',
        help="Each product asset will have a unique running sequence"
    )
    asset = fields.Boolean(
        string='Is Asset',
        default=False,
    )
    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Asset Category',
    )
    stock_valuation_account_id = fields.Many2one(
        'account.account',
        string='Stock Asset Valuation Account',
        related='asset_category_id.account_asset_id',
        readonly=True,
        help="If this product is an asset class, it will imply the stock "
        "valuation account from its assset category. ",
    )

    @api.onchange('asset')
    def _onchange_asset(self):
        self.asset_category_id = False
        self.categ_id = False

    @api.onchange('asset_category_id')
    def _onchange_asset_category_id(self):
        self.sequence_id = False
        self.categ_id = self.asset_category_id.product_categ_id

    @api.multi
    @api.constrains('asset_category_id', 'categ_id')
    def _check_category(self):
        for rec in self:
            if rec.asset_category_id and \
                    rec.categ_id != rec.asset_category_id.product_categ_id:
                raise ValidationError(
                    _('Internal Category not conform with Asset Category!'))

    @api.model
    def get_product_accounts(self, product_id):
        res = super(ProductTemplate, self).get_product_accounts(product_id)
        product = self.browse(product_id)
        if product.stock_valuation_account_id:
            res['property_stock_valuation_account_id'] = \
                product.stock_valuation_account_id.id
        return res
