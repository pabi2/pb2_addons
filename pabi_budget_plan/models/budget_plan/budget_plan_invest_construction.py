# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon, PrevFYCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon


class BudgetPlanInvestConstruction(BPCommon, models.Model):
    _name = 'budget.plan.invest.construction'
    _inherit = ['mail.thread']
    _description = "Investment Construction Budget - Budget Plan"
    _order = 'fiscalyear_id desc, id desc'

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    # Select Dimension - ORG
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
    # Master Datas
    master_org_ids = fields.Many2many(
        'res.org',
        sring='Orgs Master Data',
        compute='_compute_master_org_ids',
    )
    master_employee_ids = fields.Many2many(
        'hr.employee',
        sring='Employee Master Data',
        compute='_compute_master_employee_ids',
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(org_id, fiscalyear_id)',
         'Duplicated budget plan for the same org is not allowed!'),
    ]

    @api.multi
    def _compute_master_org_ids(self):
        Org = self.env['res.org']
        for rec in self:
            rec.master_org_ids = Org.search([('special', '=', False)])

    @api.multi
    def _compute_master_employee_ids(self):
        Employee = self.env['hr.employee']
        for rec in self:
            employees = Employee.search([('org_id', '=', rec.org_id.id),
                                         ('id', '!=', 1),
                                         ('employee_code', '!=', False)],
                                        order='employee_code')
            rec.master_employee_ids = employees

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.org', res_id=vals['org_id'])
        vals.update({'name': name})
        return super(BudgetPlanInvestConstruction, self).create(vals)

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('org_id')._ids
        # Find sections
        orgs = self.env['res.org'].search([('id', 'not in', _ids),
                                           ('special', '=', False)])
        plan_ids = []
        for org in orgs:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'org_id': org.id,
                                'user_id': False})
            plan_ids.append(plan.id)

        # Special for Invest Construction, also create budget control too
        self.env['account.budget'].\
            generate_invest_construction_controls(fiscalyear_id)

        return plan_ids


class BudgetPlanInvestConstructionLine(BPLMonthCommon, ActivityCommon,
                                       models.Model):
    _name = 'budget.plan.invest.construction.line'
    _description = "Investment Construction Budget - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='invest_construction',  # Investment Construction
    )
    plan_id = fields.Many2one(
        'budget.plan.invest.construction',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    org_id = fields.Many2one(
        related='plan_id.org_id',
        store=True,
        readonly=True,
    )
    c_or_n = fields.Selection(
        [('continue', u'ต่อเนื่อง'),
         ('new', u'ใหม่')],
        string='C/N',
        default='new',
    )
    # From Project Construction Master Data
    month_duration = fields.Integer(
        string='Months',
    )
    date_start = fields.Date(
        string='Project Start Date',
    )
    date_end = fields.Date(
        string='Project End Date',
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
    )
    pm_section_id = fields.Many2one(
        'res.section',
        string='Owner Section',
    )
    operation_area = fields.Char(
        string='Operation Area',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    project_readiness = fields.Text(
        string='Project Readiness',
    )
    reason = fields.Text(
        string='Reason',
    )
    expected_result = fields.Text(
        string='Expected Result',
    )
    amount_budget = fields.Float(
        string='Overall Budget',
    )
    amount_before = fields.Float(
        string='Before FY1',
    )
    amount_fy1 = fields.Float(
        string='FY1',
    )
    amount_fy2 = fields.Float(
        string='FY2',
    )
    amount_fy3 = fields.Float(
        string='FY3',
    )
    amount_fy4 = fields.Float(
        string='FY4',
    )
    amount_beyond = fields.Float(
        string='FY5 and Beyond',
    )
    overall_released = fields.Float(
        string='Overall Released'
    )
    overall_all_commit = fields.Float(
        string='Overall Commitment'
    )
    overall_pr_commit = fields.Float(
        string='Overall PR Commit'
    )
    overall_po_commit = fields.Float(
        string='Overall PO Commit'
    )
    overall_exp_commit = fields.Float(
        string='Overall EX Commit'
    )
    overall_actual = fields.Float(
        string='Overall Actual'
    )
    overall_consumed = fields.Float(
        string='Overall Consumed'
    )
    overall_balance = fields.Float(
        string='Overall Balance'
    )
    next_fy_commitment = fields.Float(
        string='Next FY Commitment',
    )
    # Special for Invest Construction, m1 always equal fy1
    # So, the fy1 amount will be presented in budget plan
    m1 = fields.Float(
        related='amount_fy1',
        store=True,
    )
    # Required for updating dimension
    # FIND ONLY WHAT IS NEED AND USE related field.

    @api.onchange('c_or_n')
    def _onchange_c_or_n(self):
        if self.c_or_n == 'new':
            self.invest_construction_id = False

    @api.multi
    def edit_invest_construction(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_plan.'
            'act_budget_plan_invest_construction_line_view')
        result = action.read()[0]
        view = self.env.ref('pabi_budget_plan.'
                            'view_budget_plan_invest_construction_line_form')
        result.update(
            {'res_id': self.id,
             'view_id': False,
             'view_mode': 'form',
             'views': [(view.id, 'form')],
             'context': False, })
        return result


class BudgetPlanInvestConstructionPrevFYView(PrevFYCommon, models.Model):
    """ Prev FY Performance view, must named as [model]+perv.fy.view """
    _name = 'budget.plan.invest.construction.prev.fy.view'
    _auto = False
    _description = 'Prev FY budget performance for construction'
    # Extra variable for this view
    _chart_view = 'invest_construction'
    _ex_view_fields = ['invest_construction_id', 'org_id']
    _ex_domain_fields = ['org_id']  # Each plan is by this domain
    _ex_active_domain = \
        [('invest_construction_id.state', '=', 'approve')]
    _filter_fy = False

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Construction',
        readonly=True,
    )

    @api.multi
    def _prepare_prev_fy_lines(self):
        """ Given search result from this view, prepare lines tuple """
        plan_lines = []
        Project = self.env['res.invest.construction']
        ProjectLine = self.env['budget.plan.invest.construction.line']
        project_fields = set(Project._fields.keys())
        plan_line_fields = set(ProjectLine._fields.keys())
        common_fields = list(project_fields & plan_line_fields)
        plan_fiscalyear_id = self._context.get('plan_fiscalyear_id')
        for rec in self:
            val = {
                'c_or_n': 'continue',
                'invest_construction_id': rec.invest_construction_id.id,
            }
            # Project Info, if any
            for field in common_fields:
                if field in rec.invest_construction_id and \
                        field not in ['id', '__last_update',
                                      'write_uid', 'write_date',
                                      'create_uid', 'create_date',
                                      'state', ]:
                    try:
                        val[field] = rec.invest_construction_id[field].id
                    except:
                        val[field] = rec.invest_construction_id[field]

            # Next FY Commitment
            construction = rec.invest_construction_id
            next_fy_ex = construction.monitor_expense_ids.filtered(
                lambda l: l.fiscalyear_id.id == plan_fiscalyear_id)
            next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
                                 next_fy_ex.mapped('amount_po_commit') +
                                 next_fy_ex.mapped('amount_exp_commit'))

            # Overall budget performance
            val.update({
                'overall_released': rec.released,
                'overall_all_commit': rec.all_commit,
                'overall_pr_commit': rec.pr_commit,
                'overall_po_commit': rec.po_commit,
                'overall_exp_commit': rec.exp_commit,
                'overall_actual': rec.actual,
                'overall_consumed': rec.consumed,
                'overall_balance': rec.balance,
                'next_fy_commitment': next_fy_commit
            })
            plan_lines.append((0, 0, val))
        return plan_lines
