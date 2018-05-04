# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

ACTION_TYPES = {
    'changeowner': {
        'model': 'account.asset.changeowner',
        'header_map': {  # Must be lowercase
            'id': 'id',
            'asset': 'changeowner_ids/asset_id',
            'section': 'changeowner_ids/section_id',
            'project': 'changeowner_ids/project_id',
            'location': 'changeowner_ids/location_id',
            'room': 'changeowner_ids/room',
            'responsible user': 'changeowner_ids/responsible_user_id',
        },
        'extra_columns': [],
        'action_xml': 'pabi_asset_management.action_account_asset_changeowner',
        'import_template': 'pabi_asset_management.asset_changeowner_template',
    },
    'receive': {
        'model': 'stock.picking',
        'header_map': {  # Must be lowercase
            'id': 'id',
            'supplier': 'partner_id',
            'purchase method': 'asset_purchase_method_id',
            'asset type': 'move_lines/product_id',
            'asset name': 'move_lines/name',
            'quantity': 'move_lines/product_uom_qty',
            'asset value': 'move_lines/asset_value',
            'budget': 'move_lines/chartfield_id',
            'fund': 'move_lines/fund_id',
        },
        'extra_columns': [
            ('picking_type_id/id',
             'pabi_asset_management.picking_type_asset_direct_receive'),
            ('move_lines/product_uom/id', 'product.product_uom_unit'),
            ('move_lines/location_id/id', 'stock.stock_location_suppliers'),
            ('move_lines/location_dest_id/id',
             'pabi_asset_management.stock_location_assets'),
        ],
        'action_xml': 'pabi_asset_management.action_asset_direct_receive',
        'import_template': 'pabi_asset_management.asset_receive_template',
    },
    'transfer': {
        'model': 'account.asset.transfer',
        'header_map': {  # Must be lowercase
            'id': 'id',
            'source asset(s)': 'asset_ids',
            'target asset': 'target_asset_ids/product_id',
            'target asset name': 'target_asset_ids/asset_name',
            'asset value': 'target_asset_ids/depreciation_base',
        },
        'extra_columns': [],
        'action_xml': 'pabi_asset_management.action_account_asset_transfer',
        'import_template': 'pabi_asset_management.asset_transfer_template',
    },
    'removal': {
        'model': 'account.asset.removal',
        'header_map': {  # Must be lowercase
            'id': 'id',
            'asset': 'removal_asset_ids/asset_id',
            'removal date': 'removal_asset_ids/date_remove',
            'removal entry policy': 'removal_asset_ids/posting_regime',
            'plus-value account': 'removal_asset_ids/account_plus_value_id',
            'min-value account': 'removal_asset_ids/account_min_value_id',
            'residual value account':
            'removal_asset_ids/account_residual_value_id',
            'sale value': 'removal_asset_ids/sale_value',
            'asset sale account': 'removal_asset_ids/account_sale_id',
            'asset status': 'removal_asset_ids/target_status',
        },
        'extra_columns': [],
        'action_xml': 'pabi_asset_management.action_account_asset_removal',
        'import_template': 'pabi_asset_management.asset_removal_template',
    },
}


class AssetActionExcelImport(models.TransientModel):
    _name = 'asset.action.excel.import'

    action_type = fields.Selection(
        [('changeowner', 'Change Owner'),
         ('transfer', 'Transfer'),
         ('removal', 'Removal'),
         ('receive', 'Direct Receive'),
         ],
        string='Action Type',
        required=True,
    )
    import_file = fields.Binary(
        string='Import File (*.xls)',
        required=True,
    )
    import_attachment = fields.Many2one(
        'ir.attachment',
        string='Import Attachment',
        readonly=True,
    )
    import_template = fields.Binary(
        string='Sample Import Template',
        related='import_attachment.datas',
        readonly=True,
    )
    import_template_name = fields.Char(
        string='Template Name',
        related='import_attachment.name',
        readonly=True,
    )

    @api.onchange('action_type')
    def _onchange_action_type(self):
        xml_id = self.action_type and \
            ACTION_TYPES[self.action_type].get('import_template', False)
        self.import_attachment = xml_id and self.env.ref(xml_id) or False

    @api.multi
    def action_import_xls(self):
        self.ensure_one()
        if not self.import_file:
            raise ValidationError(
                _('Please choose excel file to import!'))
        if self.action_type not in ACTION_TYPES.keys():
            raise ValidationError(
                _('Selected action type is not yet implemented'))
        model = ACTION_TYPES[self.action_type]['model']
        header_map = ACTION_TYPES[self.action_type].get('header_map', False)
        extra_columns = ACTION_TYPES[self.action_type].get('extra_columns',
                                                           False)
        xml_ids = self.env['pabi.utils.xls'].\
            import_xls(model, self.import_file,
                       header_map=header_map, extra_columns=extra_columns)
        res_ids = [self.env.ref(xmlid).id for xmlid in xml_ids]
        return self._open_imported_records(model, res_ids)

    @api.model
    def _open_imported_records(self, model, res_ids):
        action = self.env.ref(ACTION_TYPES[self.action_type]['action_xml'])
        result = action.read()[0]
        dom = [('id', 'in', res_ids)]
        result.update({'domain': dom})
        return result
