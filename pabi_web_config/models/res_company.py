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

    # PABIWeb
    pabiweb_active = fields.Boolean(
        string="Open Connection to PABI Web.",
    )
    pabiweb_pd_inactive = fields.Boolean(
        string="Disable PD Interface.",
    )
    pabiweb_hr_url = fields.Char(
        string='PABI Web URL for HR Salary',
        size=500,
    )
    pabiweb_exp_url = fields.Char(
        string='PABI Web URL for Expense',
        size=500,
    )
    pabiweb_pcm_url = fields.Char(
        string='PABI Web URL for Procurement',
        size=500,
    )
    pabiweb_file_prefix = fields.Char(
        string='PABI Web URL for attachment prefix',
        size=500,
    )
    # e-HR
    pabiehr_active = fields.Boolean(
        string='Open Connection to e-HR Webservice',
        size=500,
    )
    pabiehr_login_url = fields.Char(
        string='e-HR Login URL',
    )
    pabiehr_user = fields.Char(
        string='e-HR Login',
        size=500,
    )
    pabiehr_password = fields.Char(
        string='e-HR Password',
        size=500,
    )
    pabiehr_data_url = fields.Char(
        string='e-HR Data Retrival URL',
        size=500,
    )
    pabiehr_data_mapper = fields.Text(
        string='Odoo & e-HR Mapper Dict',
        size=100,
    )
    pabiehr_negate_code = fields.Char(
        string='Negate Codes',
        size=500,
    )
