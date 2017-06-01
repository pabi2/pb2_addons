# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartFieldAction


class AccountAssetAsset(ChartFieldAction, models.Model):
    _inherit = 'account.asset.asset'
    # _inherit = ['mail.thread', 'account.asset.asset']

    code = fields.Char(
        string='Code',  # Rename
        required=True,
        default='/',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Asset Type',
        domain=[('asset_category_id', '!=', False)],
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="This asset is created from this product class",
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Move',
        readonly=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        related='move_id.picking_id',
        store=True,
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        related='move_id.purchase_line_id.order_id',
        store=True,
        readonly=True,
    )
    no_depreciation = fields.Boolean(
        string='No Depreciation',
        related='category_id.no_depreciation',
        readonly=True,
    )
    # Additional Info
    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # section_id = fields.Many2one(
    #     'res.section',
    #     string='Section',
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    # )
    # org_id = fields.Many2one(
    #     'res.org',
    #     releated='section_id.org_id',
    #     string='Org',
    #     readonly=True,
    # )
    purchase_value = fields.Float(
        default=0.0,  # to avoid false
    )
    requester = fields.Many2one(
        'res.users',
        string='Requester',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Building',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    room = fields.Char(
        string='Room',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    serial_number = fields.Char(
        string='Serial Number',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    warranty = fields.Integer(
        string='Warranty (Month)',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    _sql_constraints = [('code_uniq', 'unique(code)',
                         'Asset Code must be unique!')]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            sequence = False
            product_id = vals.get('product_id', False)
            if product_id:
                product = self.env['product.product'].browse(product_id)
                sequence = product.sequence_id
                if not sequence:
                    raise ValidationError(
                        _('No asset sequence setup for selected product!'))
                vals['code'] = self.env['ir.sequence'].next_by_id(sequence.id)
        res = super(AccountAssetAsset, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.code and record.code != '/':
                name = "[%s] %s" % (record.code, record.name)
            else:
                name = record.name
            res.append((record.id, name))
        return res

    @api.multi
    def compute_depreciation_board(self):
        assets = self.filtered(lambda l: not l.no_depreciation)
        return super(AccountAssetAsset, assets).compute_depreciation_board()


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    product_categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        ondelete='restrict',
        required=True,
        help="Grouping of this asset category",
    )
    account_asset_id = fields.Many2one(
        domain=[('type', '=', 'other'), ('user_type.for_asset', '=', True)],
    )
    no_depreciation = fields.Boolean(
        string='No Depreciation',
        default=False,
    )

    @api.multi
    def write(self, vals):
        res = super(AccountAssetCategory, self).write(vals)
        if 'product_categ_id' in vals:
            Product = self.env['product.product']
            for asset_categ in self:
                products = Product.search([
                    ('asset', '=', True),
                    ('asset_category_id', '=', asset_categ.id)])
                products.write({'categ_id': asset_categ.product_categ_id.id})
        return res
