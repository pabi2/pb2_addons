# -*- coding: utf-8 -*-
##########################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    financial_asset = fields.Boolean(string='Is a financial Asset')


class StockMove(models.Model):
    _inherit = 'stock.move'

    generate_asset = fields.Boolean(string='Generate Asset',)

    @api.multi
    def write(self, vals):
        asset_obj = self.env['account.asset.asset']
        asset_categ_obj = self.env['account.asset.category']
        result = super(StockMove, self).write(vals)
        for move in self:
            asset_ids = []
            asset_ids = asset_obj.search(
                [('prodlot_id', '=', move.lot_ids.id)], limit=1)
            if (move.state == 'done' and not asset_ids and
                (move.generate_asset is True or
                 move.product_id.financial_asset is True)):
                #  Initialization
                date = move.date
                partner_id = False
                purchase_value = 0
                if move.purchase_line_id:
                    purchase_value = move.purchase_line_id.price_unit
                    date = move.purchase_line_id.date_planned
                else:
                    purchase_value = move.product_id.standard_price
                # Move of date asset on rely
                if move.picking_id and move.purchase_line_id.order_id and \
                        move.purchase_line_id.order_id.partner_id:
                    partner_id = move.purchase_line_id.order_id.partner_id.id
                elif move.picking_id and move.picking_id.partner_id:
                    partner_id = move.picking_id.partner_id.id
                company_id = self.env.user.company_id.id
                category_ids = asset_categ_obj.search(
                    [('company_id', '=', company_id)], limit=1)
                if category_ids:
                    category_id = category_ids[0]
                else:
                    category_id = self.env.ref(
                        "stock_asset.account_asset_category_misc_operational"
                    )
                # Process #
                create_vals = {
                    'name': move.product_id.name,
                    'category_id': category_id.id or False,
                    'code': move.lot_ids.name or False,
                    'purchase_value': purchase_value,
                    'purchase_date': date,
                    'partner_id': partner_id,
                    'product_id': move.product_id and
                    move.product_id.id or False,
                    'prodlot_id': move.lot_ids and
                    move.lot_ids.id or False,
                    'move_id': move.id,
                    'picking_id': move.picking_id and
                    move.picking_id.id or False,
                    'state': 'draft',
                }
                qty = move.product_qty
                while qty > 0:
                    qty -= 1
                    asset_obj.create(create_vals)
        return result


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    move_id = fields.Many2one(
        'stock.move',
        string='Move',
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
    )
    prodlot_id = fields.Many2one(
        'stock.production.lot',
        string='Production Lot',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    _sql_constraints = [(
        'prodlot_unique',
        'unique (prodlot_id,company_id)',
        'This prodlot is already link to an asset !'
    )]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
