# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetPlanReport(models.Model):
    _name = 'budget.plan.report'
    _auto = False

    user_id = fields.Many2one(
        'res.users',
        string='User',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    doc_ref = fields.Char(
        string='Budget Document',
    )
    budget_id = fields.Many2one(
        'account.budget',
        string='Budget Document',
    )
    m0 = fields.Float(
        string='0',
    )
    m1 = fields.Float(
        string='1',
    )
    m2 = fields.Float(
        string='2',
    )
    m3 = fields.Float(
        string='3',
    )
    m4 = fields.Float(
        string='4',
    )
    m5 = fields.Float(
        string='5',
    )
    m6 = fields.Float(
        string='6',
    )
    m7 = fields.Float(
        string='7',
    )
    m8 = fields.Float(
        string='8',
    )
    m9 = fields.Float(
        string='9',
    )
    m10 = fields.Float(
        string='10',
    )
    m11 = fields.Float(
        string='11',
    )
    m12 = fields.Float(
        string='12',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )
    released_amount = fields.Float(
        string='Released Amount',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'Confirmed'),
         ('validate', 'Validated'),
         ('done', 'Done')],
        string='Status',
    )

    def _get_sql_view(self):
        sql_view = """
            select abl.id, ab.creating_user_id as user_id, abl.fiscalyear_id,
                ab.name as doc_ref, ab.id as budget_id,
                -- Amount
                m0,
                m1, m2, m3, m4, m5, m6, m7, m8,
                m9, m10, m11, m12, abl.planned_amount, abl.released_amount,
                abl.budget_state as state,
                -- Dimensions
                %s
            from account_budget_line abl
            join account_budget ab on ab.id = abl.budget_id
        """ % (self._get_dimension(),)
        return sql_view

    def _get_dimension(self):
        return 'abl.activity_group_id, abl.activity_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
