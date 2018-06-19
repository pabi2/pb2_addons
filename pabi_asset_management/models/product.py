# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Asset Sequence',
        domain=[('special_type', '=', 'asset')],
        help="Each product asset will have a unique running sequence"
    )
    asset = fields.Boolean(
        string='Is Asset',
        default=False,
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        string='Asset Profile',
    )
    stock_valuation_account_id = fields.Many2one(
        'account.account',
        string='Stock Asset Valuation Account',
        related='asset_profile_id.account_asset_id',
        readonly=True,
        help="If this product is an asset class, it will imply the stock "
        "valuation account from its assset category. ",
    )

    @api.onchange('asset')
    def _onchange_asset(self):
        self.asset_profile_id = False
        self.categ_id = False

    @api.onchange('asset_profile_id')
    def _onchange_asset_profile_id(self):
        self.sequence_id = False
        self.categ_id = self.asset_profile_id.product_categ_id

    @api.multi
    @api.constrains('asset_profile_id', 'categ_id')
    def _check_category(self):
        for rec in self:
            if rec.asset_profile_id and \
                    rec.categ_id != rec.asset_profile_id.product_categ_id:
                raise ValidationError(
                    _('Internal Category not conform with Asset Category!'))

    @api.model
    def get_product_accounts(self, product_id):
        """ Overwrite
        To get the stock input account, stock output account and stock
        journal related to product.
        @param product_id: product id
        @return: dictionary which contains information regarding stock input
                 account, stock output account and stock journal
        """
        product = self.browse(product_id)
        stock_input_acc = product.property_stock_account_input or \
            product.categ_id.property_stock_account_input_categ
        stock_output_acc = product.property_stock_account_output or \
            product.categ_id.property_stock_account_output_categ
        journal = product.categ_id.property_stock_journal
        account_valuation = product.stock_valuation_account_id or \
            product.categ_id.property_stock_valuation_account_id
        if not all([stock_input_acc, stock_output_acc,
                    account_valuation, journal]):
            raise ValidationError(
                _('One of the following information is missing on the product '
                  'or product category and prevents the accounting valuation '
                  'entries to be created:\n'
                  'Product: %s\n'
                  'Stock Input Account: %s\n'
                  'Stock Output Account: %s\n'
                  'Stock Valuation Account: %s\n'
                  'Stock Journal: %s') %
                (product.name,
                 stock_input_acc.code,
                 stock_output_acc.code,
                 account_valuation.code,
                 journal.name))
        return {
            'stock_account_input': stock_input_acc.id,
            'stock_account_output': stock_output_acc.id,
            'stock_journal': journal.id,
            'property_stock_valuation_account_id': account_valuation.id
        }
