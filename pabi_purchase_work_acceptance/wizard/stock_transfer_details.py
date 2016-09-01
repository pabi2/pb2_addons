# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This progfram is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        Picking = self.env['stock.picking']
        picking_ids = self.env.context['active_ids'] or []
        picking = Picking.browse(picking_ids)
        res = super(StockTransferDetails, self).default_get(fields)
        if picking.picking_type_code == 'incoming':
            new_item_ids = []
            for item in res['item_ids']:
                new_qty = 0
                for wa_line in picking.acceptance_id.acceptance_line_ids:
                    if wa_line.product_id.id == item['product_id']:
                        new_qty += wa_line.to_receive_qty
                item['quantity'] = new_qty
                new_item_ids.append(item)
            res['item_ids'] = new_item_ids
        return res
