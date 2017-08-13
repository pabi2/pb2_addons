# -*- coding: utf-8 -*-
import ast
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class CreateAssetAdjustWizard(models.TransientModel):
    _name = 'create.asset.adjust.wizard'

    adjust_type = fields.Selection(
        [('asset_type', 'Change Asset Type')],
        string='Type of Adjustment',
        required=True,
    )
    adjust_asset_type_ids = fields.One2many(
        'asset.adjust.asset.type',
        'wizard_id',
        string='Adjust Asset Type',
    )

    @api.model
    def view_init(self, fields_list):
        invoice_id = self._context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        if invoice.state not in ('open', 'paid'):
            raise ValidationError(
                _('Only open invoice allowed!'))

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
        adjust_asset_types = [(x.from_product_id.id, x.to_product_id.id)
                              for x in self.adjust_asset_type_ids]
        ctx.update({'default_adjust_type': self.adjust_type,
                    'default_invoice_id': invoice_id,
                    'adjust_asset_type_dict': dict(adjust_asset_types)})
        result['context'] = ctx
        return result

    @api.onchange('adjust_type')
    def _onchange_adjust_type(self):
        self.adjust_asset_type_ids = False
        if not self.adjust_type:
            return
        if self.adjust_type == 'asset_type':
            Invoice = self.env['account.invoice']
            Asset = self.env['account.asset']
            invoice = Invoice.browse(self._context.get('active_id', False))
            invoice_lines = invoice.invoice_line
            if invoice_lines:
                asset_lines = invoice_lines.filtered('product_id.asset')
                asset_moves = asset_lines.mapped('move_id')
                asset_picks = asset_moves.mapped('picking_id')
                assets = Asset.search([('picking_id', 'in', asset_picks.ids)])
                asset_types = assets.mapped('product_id')
                for asset_type in asset_types:
                    line = self.env['asset.adjust.asset.type'].new()
                    line.from_product_id = asset_type
                    self.adjust_asset_type_ids += line


class AssetAdjustAssetType(models.TransientModel):
    _name = 'asset.adjust.asset.type'

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
