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


class StockMove(models.Model):
    _inherit = 'stock.move'

    generate_asset = fields.Boolean(string='Generate Asset',)

    @api.multi
    def _assign_lot_by_category(self):
        return True

    @api.multi
    def write(self, vals):
        self._assign_lot_by_category()
        res = super(StockMove, self).write(vals)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
