# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (C) 2016 Savoir-faire Linux
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
##############################################################################

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_move_by_taxbranch = fields.Boolean(
        string="Tax Account Move by Tax Branch",
    )
    wht_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string="Taxbranch for Withholding Tax",
    )
    bank_ids = fields.One2many(
        domain=['|', ('active', '=', False), ('active', '=', True)],
    )
    #AR email
    group_email_ar = fields.Char(
        string='AR E-mail',
        default='acf-adv@nstda.or.th',
        size=500,
    )
    ar_send_to_groupmail_only = fields.Boolean(
        string='Send to groupmail only',
        default=False,
    )