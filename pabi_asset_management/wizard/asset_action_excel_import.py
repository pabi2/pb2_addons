# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

ACTION_TYPES = {
    'change_owner': {
        'model': 'account.asset.changeowner',
        'header_map': {
            'id': 'id',
            'asset': 'changeowner_ids/asset_id',
            'section': 'changeowner_ids/section_id',
            'project': 'changeowner_ids/project_id',
            'location': 'changeowner_ids/location_id',
            'room': 'changeowner_ids/room',
            'responsible user': 'changeowner_ids/responsible_user_id',
        },
        'action_xml': 'pabi_asset_management.'
                      'action_account_asset_changeowner_form',
    },
    'direct_receive': {
        'model': 'stock.picking',
        'header_map': {
            'id': 'id',
            'supplier': 'partner_id',
            'purchase method': 'asset_purchase_method_id',
            'asset type': 'move_lines/product_id/id',  # STILL NOT name_search
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
    },
}


class AssetActionExcelImport(models.TransientModel):
    _name = 'asset.action.excel.import'

    action_type = fields.Selection(
        [('change_owner', 'Change Asset Owner'),
         ('direct_receive', 'Direct Receive Asset'),
         ('transfer', 'Asset Transfer'),
         ('removal', 'Asset Removal')],
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
        related='import_attachment.datas',
        string='Sample Import File',
        readonly=True,
    )

    @api.onchange('action_type')
    def _onchange_action_type(self):
        self.import_attachment = self.env.ref(
            'pabi_asset_management.asset_changeowner_template')

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
        xml_ids = self.env['pabi.xls'].import_xls(model, self.import_file,
                                                  header_map=header_map,
                                                  extra_columns=extra_columns)
        res_ids = [self.env.ref(xmlid).id for xmlid in xml_ids]
        return self._open_imported_records(model, res_ids)

    @api.model
    def _open_imported_records(self, model, res_ids):
        action = self.env.ref(ACTION_TYPES[self.action_type]['action_xml'])
        result = action.read()[0]
        dom = [('id', 'in', res_ids)]
        result.update({'domain': dom})
        return result
