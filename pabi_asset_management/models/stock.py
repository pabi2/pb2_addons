# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    donor = fields.Char(
        string='Donor',
    )
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

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.donor = False

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
    @api.constrains('asset_purchase_method_id', 'move_lines')
    def _check_chartfield_id(self):
        for rec in self:
            if not rec.asset_purchase_method_id:
                continue
            # TODO: user says, though donation it will require costcenter
            # Just no budget.
            # elif rec.asset_purchase_method_id.code == '8':  # Donation
            #     if rec.move_lines.filtered('chartfield_id'):
            #         raise ValidationError(
            #             _("For Donation, budget is not required!"))
            else:
                if rec.move_lines.filtered(lambda l: not l.chartfield_id):
                    raise ValidationError(
                        _('Budget is required for all assets'))


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
    building_id = fields.Many2one(
        'res.building',
        string='Building',
        ondelete='restrict',
    )
    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
        ondelete='restrict',
    )
    room_id = fields.Many2one(
        'res.room',
        string='Room',
        ondelete='restrict',
    )

    # Building / Floor / Room
    # @api.multi
    # @api.constrains('building_id', 'floor_id', 'room_id')
    # def _check_building(self):
    #     for rec in self:
    #         self.env['res.building']._check_room_location(rec.building_id,
    #                                                       rec.floor_id,
    #                                                       rec.room_id)

    @api.model
    def create(self, vals):
        print '=======WRITE START======'
        print vals
        import time
        start = time.time()
        res = super(StockMove, self).create(vals)
        end = time.time()
        print '=======CREATE========> %s' % (end - start)
        return res

    @api.multi
    def write(self, vals):
        print '=======WRITE START======'
        print vals
        import time
        start = time.time()
        res = super(StockMove, self).write(vals)
        end = time.time()
        print '=======WRITE========> %s' % (end - start)
        return res

    @api.multi
    @api.depends('asset_value', 'product_uom_qty')
    def _compute_asset_value_total(self):
        for rec in self:
            rec.asset_value_total = rec.product_uom_qty * rec.asset_value
