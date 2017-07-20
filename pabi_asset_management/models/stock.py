# -*- coding: utf-8 -*-
from openerp import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    asset_ids = fields.One2many(
        'account.asset',
        'picking_id',
        string='Assets',
        readonly=True,
    )
    asset_count = fields.Integer(
        string='Asset Count',
        compute='_compute_assset_count',
    )
    asset_purchase_method_id = fields.Many2one(
        'asset.purchase.method',
        string='Aquisition Method',
        help="In case of direct receive, user will manually choose it."
    )

    @api.multi
    def action_view_asset(self):
        self.ensure_one()
        Asset = self.env['account.asset']
        action = self.env.ref('account_asset_management.account_asset_action')
        result = action.read()[0]
        assets = Asset.with_context(active_test=False).search([('picking_id',
                                                                '=', self.id)])
        dom = [('id', 'in', assets.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    @api.depends()
    def _compute_assset_count(self):
        for rec in self:
            rec.asset_count = len(rec.asset_ids)

    @api.multi
    def open_entries(self):
        self.ensure_one()
        moves = self.env['account.move'].search(
            [('document', '=', self.name)], order='date ASC')
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', moves.ids)],
        }

    @api.multi
    def action_confirm_and_transfer(self):
        self.ensure_one()
        self = self.with_context(skip_work_acceptance=True)
        self.action_confirm()
        return self.do_enter_transfer_details()


class StockMove(models.Model):
    _inherit = 'stock.move'

    asset_value = fields.Float(
        string='Asset Value (each)',
        help="Case direct receive, need to spcifiy asset value",
    )
    asset_value_total = fields.Float(
        string='Total Value',
        compute='_compute_asset_value_total',
    )

    @api.multi
    @api.depends('asset_value', 'product_uom_qty')
    def _compute_asset_value_total(self):
        for rec in self:
            rec.asset_value_total = rec.product_uom_qty * rec.asset_value
