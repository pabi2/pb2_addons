# -*- coding: utf-8 -*-
from openerp import api, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        dest_ou_id = self.picking_type_id.warehouse_id.operating_unit_id.id
        User = self.env['res.users']
        users = User.search([('operating_unit_ids', 'in', dest_ou_id)])
        if not dest_ou_id:
            return []
        return {
            'domain': {
                'receive_emp_id': [
                    ('user_id', 'in', users._ids),
                ]
            }
        }
