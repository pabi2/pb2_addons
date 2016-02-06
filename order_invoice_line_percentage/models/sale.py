# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields, api


class sale_order(models.Model):

    _inherit = 'sale.order'

    price_include = fields.Boolean(
        string='Tax Included in Price',
        readonly=True,
        compute="_price_include")

    @api.one
    @api.depends('order_line.tax_id')
    def _price_include(self):
        self.price_include = self.order_line and \
            self.order_line[0].tax_id and \
            self.order_line[0].tax_id[0].price_include or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
