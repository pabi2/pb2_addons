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

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_deposit_customer = fields.Many2one(
        'account.account',
        string="Account Advance Customer",
        company_dependent=True,
        view_load=True,
        domain="[('type', '!=', 'view')]",
        required=True,
        readonly=True,
        help="This account will be used instead of the "
        "default one as the advance account for the current partner")
