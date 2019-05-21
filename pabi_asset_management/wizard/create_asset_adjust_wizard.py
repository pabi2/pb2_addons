# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CreateAssetAdjustWizard(models.TransientModel):
    _name = 'create.asset.adjust.wizard'

    adjust_type = fields.Selection(
        [('asset_type', 'Asset => Asset'),
         ('asset_to_expense', 'Asset => Expense'),
         ('expense_to_asset', 'Expense => Asset')],
        string='Type of Adjustment',
        required=True,
    )
    source_document_type = fields.Selection(
        [('purchase', 'Purchase Order'),
         ('sale', 'Sales Order'),
         ('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Type',
    )
    ship_purchase_id = fields.Many2one(
        'purchase.order',
        string='Ship Expense For PO',
        domain="[('order_type', '=', 'purchase_order'),"
        "('state', 'not in', ('draft', 'cancel'))]",
        help="This expense is shipping handling for things bought "
        "with this purchase order.",
    )
    adjust_asset_type_ids = fields.One2many(
        'adjust.asset.type',
        'wizard_id',
        string='Adjust Asset Type',
    )
    asset_to_expense_ids = fields.One2many(
        'asset.to.expense',
        'wizard_id',
        string='Asset => Expense',
    )
    expense_to_asset_ids = fields.One2many(
        'expense.to.asset',
        'wizard_id',
        string='Expense => Asset',
    )

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.state not in ('open', 'paid'):
            raise ValidationError(
                _('Only open invoice allowed!'))
        if invoice.asset_adjust_id:
            raise ValidationError(
                _('The asset adjustment already created!'))

    @api.model
    def default_get(self, fields):
        res = super(CreateAssetAdjustWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(active_id)
        res['source_document_type'] = invoice.source_document_type
        return res

    @api.multi
    def _validate(self):
        self.ensure_one()
        if self.adjust_type == 'asset_type':
            if not self.adjust_asset_type_ids:
                raise ValidationError(_('No asset type adjustment!'))
            if self.adjust_asset_type_ids.filtered(
                    lambda l: l.to_product_id == l.from_product_id):
                raise ValidationError(
                    _('From Asset Type and To Asset Type must be different!'))

    @api.multi
    def create_asset_adjust(self):
        self.ensure_one()
        self._validate()
        action = self.env.ref('pabi_asset_management.'
                              'action_account_asset_adjust')
        result = action.read()[0]
        view = self.env.ref('pabi_asset_management.'
                            'view_account_asset_adjust_form')
        result = action.read()[0]
        result.update({'view_mode': 'form',
                       'target': 'current',
                       'view_id': view.id,
                       'view_ids': False,
                       'views': False})
        ctx = ast.literal_eval(result['context'])
        invoice_id = self._context.get('active_id')
        # Adjust Asset Type values
        adjust_asset_types = [(x.from_product_id.id, x.to_product_id.id)
                              for x in self.adjust_asset_type_ids]
        # Asset to Expense
        asset_to_expenses = [(x.from_product_id.id, (x.account_id.id,
                                                     x.activity_group_id.id,
                                                     x.activity_id.id))
                             for x in self.asset_to_expense_ids]
        # Expense to Asset
        expense_to_assets = [(x.id, x.from_account_id.id, x.to_product_id.id,
                              x.invoice_line_id.id, x.quantity)
                             for x in self.expense_to_asset_ids]
        limit_asset_value = sum([x.invoice_line_id.price_subtotal
                                 for x in self.expense_to_asset_ids])
        ctx.update({'default_adjust_type': self.adjust_type,
                    'default_invoice_id': invoice_id,
                    'default_ship_purchase_id': self.ship_purchase_id.id,
                    'adjust_asset_type_dict': dict(adjust_asset_types),
                    'asset_to_expense_dict': dict(asset_to_expenses),
                    'expense_to_asset_dict': expense_to_assets,
                    'default_limit_asset_value': limit_asset_value})
        result['context'] = ctx
        _logger.info("------- create_asset_adjust -------")
        _logger.info("context: %s", str(result['context']))
        return result

    @api.onchange('adjust_type')
    def _onchange_adjust_type(self):
        self.adjust_asset_type_ids = False
        self.expense_to_asset_ids = False
        self.asset_to_expense_ids = False
        if not self.adjust_type:
            return
        invoice_id = self._context.get('active_id', False)
        invoice = self.env['account.invoice'].browse(invoice_id)
        TYPES = {
            'asset_type': ('adjust.asset.type', 'adjust_asset_type_ids'),
            'asset_to_expense': ('asset.to.expense', 'asset_to_expense_ids'),
            'expense_to_asset': ('expense.to.asset', 'expense_to_asset_ids'), }
        # Asset to ....
        if self.adjust_type in ('asset_type', 'asset_to_expense'):
            AssetAdjust = self.env['account.asset.adjust']
            assets = AssetAdjust.get_invoice_line_assets(invoice)
            asset_types = assets.mapped('product_id')
            for asset_type in asset_types:
                line = self.env[TYPES[self.adjust_type][0]].new()
                line.from_product_id = asset_type
                self[TYPES[self.adjust_type][1]] += line
        # Expense to Asset
        if self.adjust_type in ('expense_to_asset'):
            # inv_lines = invoice.invoice_line.filtered(lambda l:
            #                                           not l.product_id)
            inv_lines = invoice.invoice_line  # Take any line
            for inv_line in inv_lines:
                line = self.env[TYPES[self.adjust_type][0]].new()
                line.from_account_id = inv_line.account_id
                line.quantity = 1
                line.invoice_line_id = inv_line
                self[TYPES[self.adjust_type][1]] += line


class AdjustAssetType(models.TransientModel):
    _name = 'adjust.asset.type'
    # _inherit = 'account.asset.remove'

    wizard_id = fields.Many2one(
        'create.asset.adjust.wizard',
        string='Asset Adjust',
        readonly=True,
    )
    from_product_id = fields.Many2one(
        'product.product',
        string='From Asset Type',
        required=True,
        domain=[('asset', '=', True)],
    )
    to_product_id = fields.Many2one(
        'product.product',
        string='To Asset Type',
        required=True,
        domain=[('asset', '=', True)],
    )


class AssetToExpense(ActivityCommon, models.TransientModel):
    _name = 'asset.to.expense'

    wizard_id = fields.Many2one(
        'create.asset.adjust.wizard',
        string='Asset Adjust',
        readonly=True,
    )
    from_product_id = fields.Many2one(
        'product.product',
        string='From Asset Type',
        required=True,
        domain=[('asset', '=', True)],
    )
    account_id = fields.Many2one(
        'account.account',
        string='To Expense Account',
        required=True,
        domain=[('type', '!=', 'view')],
    )


class ExpenseToAsset(models.TransientModel):
    _name = 'expense.to.asset'
    # _inherit = 'account.asset.remove'

    wizard_id = fields.Many2one(
        'create.asset.adjust.wizard',
        string='Asset Adjust',
        readonly=True,
    )
    from_account_id = fields.Many2one(
        'account.account',
        string='To Expense',
        required=True,
        domain=[('type', '!=', 'view')],
    )
    to_product_id = fields.Many2one(
        'product.product',
        string='To Asset Type',
        required=True,
        domain=[('asset', '=', True)],
    )
    quantity = fields.Integer(
        string='Asset Quantity',
        required=True,
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
    )
    _sql_constraints = [
        ('positive_qty', 'check(quantity > 0)',
         'Negative quantity not allowed!')]
