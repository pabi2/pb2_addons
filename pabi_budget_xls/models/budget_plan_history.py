# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class BudgetPlanHistory(models.Model):
    _name = 'budget.plan.history'

    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        readonly=False,
    )
    operation_date = fields.Datetime(
        string="Operation Date Time",
        readonly=False,
    )
    operation_type = fields.Selection(
        [('import', 'Import'),
         ('export', 'Export'),],
        string="Operation Type",
        readonly=False,
    )
    plan_id = fields.Many2one(
        'budget.plan.unit',
        string="Budget Plan",
        readonly=False,
    )
    attachement_id = fields.Many2one(
        'ir.attachment',
        string="Attachment",
        readonly=False,
    )

