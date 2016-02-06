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


class res_partner(models.Model):

    _inherit = 'res.partner'

    property_retention_on_payment = fields.Boolean(
        string="Retention on Payment",
        company_dependent=True,
        readonly=False,
        help="""If this is checked, retention will be carried from invoice
                to payment for account posting. Otherwise on invoice.""")
    property_account_retention_customer = fields.Many2one(
        'account.account',
        string="Account Retention Customer",
        company_dependent=True,
        domain="[('type', '!=', 'view')]",
        required=False,
        readonly=True,
        help="""This account will be used instead of the default one
                as the retention account for the current partner""")
    property_account_retention_supplier = fields.Many2one(
        'account.account',
        string="Account Retention Supplier",
        company_dependent=True,
        domain="[('type', '!=', 'view')]",
        required=False,
        readonly=True,
        help="""This account will be used instead of the default one as the
                retention account for the current partner""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
