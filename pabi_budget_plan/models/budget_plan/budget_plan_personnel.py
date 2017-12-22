# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon


class BudgetPlanPersonnel(BPCommon, models.Model):
    _name = 'budget.plan.personnel'
    _inherit = ['mail.thread']
    _description = "Personnel - Budget Plan"
    _order = 'id desc'

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    # Select Dimension - Personnel
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Budget',
        required=True,
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(personnel_costcenter_id, fiscalyear_id)',
         'Duplicated budget plan for the same personnel '
         'budget is not allowed!'),
    ]

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.personnel.costcenter',
                                    vals['personnel_costcenter_id'])
        vals.update({'name': name})
        return super(BudgetPlanPersonnel, self).create(vals)

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('personnel_costcenter_id')._ids
        # Find Programs
        PersonnelCostcenter = self.env['res.personnel.costcenter']
        personnels = PersonnelCostcenter.search([('id', 'not in', _ids),
                                                 ('special', '=', False)])
        plan_ids = []
        for personnel in personnels:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'personnel_costcenter_id': personnel.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids

    @api.multi
    def convert_to_budget_control(self):
        """ Create a budget control from budget plan """
        self.ensure_one()
        head_src_model = self.env['budget.plan.personnel']
        line_src_model = self.env['budget.plan.personnel.line']
        budget = self._convert_plan_to_budget_control(self.id,
                                                      head_src_model,
                                                      line_src_model)
        return budget


class BudgetPlanPersonnelLine(BPLMonthCommon, ActivityCommon, models.Model):
    _name = 'budget.plan.personnel.line'
    _description = "Personnel - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='personnel',  # Personnel
    )
    plan_id = fields.Many2one(
        'budget.plan.personnel',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    personnel_costcenter_id = fields.Many2one(
        related='plan_id.personnel_costcenter_id',
        store=True,
        readonly=True,
    )

    # Required for updating dimension
    # FIND ONLY WHAT IS NEED AND USE related field.
