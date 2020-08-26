# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountAssetImportBatch(models.Model):
    _name = 'account.asset.import.batch'
    _inherit = ['mail.thread']
    _description = 'Import asset by batch'

    name = fields.Char(
        default='/',
        required=True,
        readonly=True,
        copy=False,
    )
    note = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        copy=False)
    asset_count = fields.Integer(
        string='# of Assets',
        compute='_compute_asset_count',
        help='Count assets in batch',
    )
    asset_ids = fields.Many2many(
        comodel_name='account.asset',
    )
    asset_batch_ids = fields.One2many(
        comodel_name='account.asset.import.batch.line',
        inverse_name='asset_batch_id',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def _compute_asset_count(self):
        self.asset_count = len(self.asset_batch_ids)

    @api.multi
    def asset_count_tree_view(self):
        self.ensure_one()
        view_id = self.env.ref(
            'pabi_asset_import_batch.account_asset_batch_view_tree', False)
        form_id = self.env.ref(
            'pabi_asset_management.account_asset_view_form', False)
        return {
            'name': _("Assets"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset',
            'views': [(view_id.id, 'tree'), (form_id.id, 'form')],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': [('id', 'in', self.asset_ids.ids)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].\
                get('account.asset.import.batch') or '/'
        return super(AccountAssetImportBatch, self).create(vals)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        asset_obj = self.env['account.asset']
        asset_line_obj = self.env['account.asset.line']
        asset_normal = self.asset_batch_ids.filtered(
            lambda l: l.profile_id.profile_type == 'normal')
        if asset_normal and not all(asset_normal.mapped('purchase_value')):
            raise ValidationError(_(
                'Can not import Asset type normal that purchase value is 0.0'))
        for line in self.asset_batch_ids:
            asset_dict = {
                'code': line.code or '/',
                'code2': line.code2,
                'name': line.name,
                'status': line.status.id,
                'is_standard': line.is_standard,
                'asset_brand': line.asset_brand,
                'asset_model': line.asset_model,
                'purchase_value': line.purchase_value,
                'salvage_value': line.salvage_value,
                'date_start': line.date_start,
                'section_id': line.section_id.id,
                'project_id': line.project_id.id,
                'invest_asset_id': line.invest_asset_id.id,
                'invest_construction_phase_id':
                line.invest_construction_phase_id.id,
                'profile_id': line.profile_id.id,
                'product_id': line.product_id.id,
                'partner_id': line.partner_id.id,
                'method_number': line.method_number,
                'owner_section_id': line.owner_section_id.id,
                'owner_project_id': line.owner_project_id.id,
                'owner_invest_asset_id': line.owner_invest_asset_id.id,
                'owner_invest_construction_phase_id':
                line.owner_invest_construction_phase_id.id,
                'asset_purchase_method_id': line.asset_purchase_method_id.id,
                'responsible_user_id': line.responsible_user_id.id,
                'room_id': line.room_id.id,
                'floor_id': line.floor_id.id,
                'building_id': line.building_id.id,
                'serial_number': line.serial_number,
                'warranty_start_date': line.warranty_start_date,
                'warranty_expire_date': line.warranty_expire_date,
                'note': line.note,
                'method_period': line.method_period,
                'days_calc': line.days_calc,
                'prorata': line.prorata,
                'is_import': True,  # True only if import asset
            }
            new_asset = asset_obj.create(asset_dict)
            # purchase_id is field related can't create
            if line.purchase_id:
                new_asset.purchase_id = line.purchase_id.id
            if new_asset.profile_type == 'normal':
                asset_line_dict = {
                    'asset_id': new_asset.id,
                    'line_date': line.line_date,
                    'line_days': line.line_days,
                    'amount': line.amount,
                    'init_entry': line.init_entry,
                }
                asset_line_obj.create(asset_line_dict)
                new_asset.compute_depreciation_board()
            new_asset.validate()
            # link to asset
            self.asset_ids += new_asset
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})


class AccountAssetImportBatchLine(models.Model):
    _name = 'account.asset.import.batch.line'
    _description = 'Asset Batch Import'

    asset_batch_id = fields.Many2one(
        comodel_name='account.asset.import.batch',
    )
    code = fields.Char(
        string='Code',
    )
    code2 = fields.Char(
        string='Code (legacy)',
    )
    name = fields.Char()
    status = fields.Many2one(
        comodel_name='account.asset.status',
        string='Asset Status',
    )
    is_standard = fields.Boolean(
        string='Standard Asset',
    )
    asset_brand = fields.Char(
        string='Brand',
    )
    asset_model = fields.Char(
        string='Model',
    )
    purchase_value = fields.Float(
        string='Purchase Value',
    )
    salvage_value = fields.Float(
        string='Salvage Value',
    )
    date_start = fields.Date(
        string='Asset Start Date'
    )
    section_id = fields.Many2one(
        comodel_name='res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        comodel_name='res.project',
        string='Project',
    )
    invest_asset_id = fields.Many2one(
        comodel_name='res.invest.asset',
        string='Invest Asset',
    )
    invest_construction_phase_id = fields.Many2one(
        comodel_name='res.invest.construction.phase',
        string='Construction Phase',
    )
    profile_id = fields.Many2one(
        comodel_name='account.asset.profile',
        string='Asset Profile',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Asset Type',
    )
    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    method_number = fields.Integer(
        string='Number of Years'
    )
    owner_section_id = fields.Many2one(
        comodel_name='res.section',
        string='Section',
    )
    owner_project_id = fields.Many2one(
        comodel_name='res.project',
        string='Project',
    )
    owner_invest_asset_id = fields.Many2one(
        comodel_name='res.invest.asset',
        string='Investment Asset',
    )
    owner_invest_construction_phase_id = fields.Many2one(
        comodel_name='res.invest.construction.phase',
        string='Construction Phase',
    )
    asset_purchase_method_id = fields.Many2one(
        comodel_name='asset.purchase.method',
        string='Purchase Method',
    )
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible Person',
    )

    room_id = fields.Many2one(
        comodel_name='res.room',
        string='Room',
    )
    floor_id = fields.Many2one(
        comodel_name='res.floor',
        string='Floor',
    )
    building_id = fields.Many2one(
        comodel_name='res.building',
        string='Building',
    )
    serial_number = fields.Char(
        string='Serial Number',
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
    )
    note = fields.Text(
        string='Note',
    )
    method_period = fields.Selection(
        selection=[('month', 'Month'),
                   ('quarter', 'Quarter'),
                   ('year', 'Year')],
        string='Period Length',
    )
    days_calc = fields.Boolean(
        string='Calculate by days',
    )
    prorata = fields.Boolean(
        string='Prorata Temporis',
    )
    line_date = fields.Date(string='Line Date')
    line_days = fields.Integer(string='Line Days')
    amount = fields.Float(string='Line Amount')
    init_entry = fields.Boolean(string='Line Init')
