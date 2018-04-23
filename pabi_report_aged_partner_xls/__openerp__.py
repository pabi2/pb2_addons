# -*- coding: utf-8 -*-
###############################################################################
#
#   report_aged_partner_xls for Odoo
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Report Aged Partner Balance XLS',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'author': "Geminate Consultancy Services",
    'category': 'Generic Modules/Accounting',
    'description': """

    This module adds XLS export to the following
    Generic Reporting > Partners reports:
        - Aged Partner Balance

    """,
    'depends': ['pabi_account_financial_report_webkit'],
    'demo': [],
    'data': [
        'wizard/aged_partner_balance_wizard.xml'
    ],
    'test': [],
    'active': True,
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
