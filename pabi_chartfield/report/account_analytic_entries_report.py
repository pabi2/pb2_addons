# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp import models, fields


class AnalyticEntriesReport(models.Model):
    _inherit = "analytic.entries.report"

    mission_id = fields.Many2one('res.mission', 'Mission')
    spa_id = fields.Many2one('res.program.spa', 'SPA')
    program_base_type_id = fields.Many2one('res.program.base.type',
                                           'Program Base Type')
    program_type_id = fields.Many2one('res.program.type', 'Program Type')
    program_id = fields.Many2one('res.program', 'Program')
    org_id = fields.Many2one('res.org', 'Org')
    project_id = fields.Many2one('res.project', 'Project')
    division_id = fields.Many2one('res.division', 'Division')
    department_id = fields.Many2one('res.department', 'Department')
    costcenter_id = fields.Many2one('res.costcenter', 'Costcenter')
    activity_id = fields.Many2one('account.activity', 'Activity')
    activity_group_id = fields.Many2one('account.activity.group',
                                        'Activity Group')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'analytic_entries_report')
        cr.execute("""
            create or replace view analytic_entries_report as (
                select
                     min(a.id) as id,
                     count(distinct a.id) as nbr,
                     a.date as date,
                     a.user_id as user_id,
                     a.name as name,
                     analytic.partner_id as partner_id,
                     a.company_id as company_id,
                     a.currency_id as currency_id,
                     a.account_id as account_id,
                     a.general_account_id as general_account_id,
                     a.journal_id as journal_id,
                     a.move_id as move_id,
                     a.product_id as product_id,
                     a.product_uom_id as product_uom_id,
                     sum(a.amount) as amount,
                     sum(a.unit_amount) as unit_amount,
                     -- new fields
                     a.mission_id,
                     a.spa_id,
                     a.program_base_type_id,
                     a.program_type_id,
                     a.program_id,
                     a.org_id,
                     a.project_id,
                     a.division_id,
                     a.department_id,
                     a.costcenter_id,
                     a.activity_group_id,
                     a.activity_id
                 from
                     account_analytic_line a, account_analytic_account analytic
                 where analytic.id = a.account_id
                 group by
                     a.date, a.user_id,a.name,analytic.partner_id,
                     a.company_id,a.currency_id,
                     a.account_id,a.general_account_id,a.journal_id,
                     a.move_id,a.product_id,a.product_uom_id,
                     -- new fields
                     a.mission_id,
                     a.spa_id,
                     a.program_base_type_id,
                     a.program_type_id,
                     a.program_id,
                     a.org_id,
                     a.project_id,
                     a.division_id,
                     a.department_id,
                     a.costcenter_id,
                     a.activity_group_id,
                     a.activity_id
            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
