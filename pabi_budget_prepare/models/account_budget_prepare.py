# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountBudgetPrepare(models.Model):
    _name = "account.budget.prepare"
    _description = "Budget Prepare"

    name = fields.Char(
        string='Name',
        required=True,
        states={'published': [('readonly', True)]},
    )
    code = fields.Char(
        string='Code',
        size=16,
        required=True,
        states={'published': [('readonly', True)]},
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    state = fields.Selection(
        [('plan', 'Draft'),
         ('cancel', 'Cancelled'),
         ('policy', 'Submited'),
         ('release', 'Approved'),
         ('publish', 'Released')],
        string='Status',
        default='plan',
        index=True,
        required=True,
        readonly=True,
        copy=False,
    )
    prepare_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Budget Prepare Lines',
        states={'publish': [('readonly', True)]},
        copy=True,
    )
    continue_prepare_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Continue Budget Prepare Lines',
        states={'publish': [('readonly', True)]},
        domain=[('project_kind', '=', 'continue')],
        copy=True,
    )
    new_prepare_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='new Budget Prepare Lines',
        states={'publish': [('readonly', True)]},
        domain=[('project_kind', '=', 'new')],
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('account.budget')
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    amount_budget_policy = fields.Float(
        string='Budget Policy',
        digits_compute=dp.get_precision('Account'),
    )
    amount_budget_release = fields.Float(
        string='Budget Release',
        digits_compute=dp.get_precision('Account'),
    )
    input_file = fields.Binary(
        string='Import myProject (.xlsx)',
    )

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def budget_release(self):
        self.write({
            'state': 'release',
            'validating_user_id': self._uid,
        })
        return True

    @api.multi
    def budget_policy(self):
        self.write({'state': 'policy'})
        return True

    @api.multi
    def budget_plan(self):
        self.write({'state': 'plan'})
        return True

    @api.multi
    def budget_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def budget_publish(self):
        self.write({'state': 'publish'})
        return True


class AccountBudgetPrepareLine(models.Model):

    _name = "account.budget.prepare.line"
    _description = "Budget Line"

    prepare_id = fields.Many2one(
        'account.budget.prepare',
        string='Budget Prepare',
        ondelete='cascade',
        index=True,
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='prepare_id.company_id',
        string='Company',
        type='many2one',
        store=True,
        readonly=True,
    )
    # Dimensions
    project_kind = fields.Selection(
        [('continue', 'Continue'),
         ('new', 'New')],
        string='C/N',
        default='new',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional_Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program_Group',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project_Group',
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
    )
    project_type = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non-Research')],
        string='Project_Type',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    main_program = fields.Char(
        string='Main_Program',
    )
    project_category = fields.Char(
        string='Project_Category',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    manager_user_id = fields.Many2one(
        'res.users',
        string='Project_Manager',
    )
    date_from = fields.Date(
        string='Start_Date',
    )
    date_to = fields.Date(
        string='End_Date',
    )
    project_duration_yr = fields.Integer(
        string='Project_Duration_(Yrs)',
    )
    project_status = fields.Char(
        string='Project_Status',
    )
    # Monetary
    planned_amount = fields.Float(
        string='Planned_Amount',
        digits_compute=dp.get_precision('Account'),
    )
    revenue_planned = fields.Float(
        string='Revenue_Planned',
        digits_compute=dp.get_precision('Account'),
    )
    revenue_to_date = fields.Float(
        string='Revenue_Actual',
        digits_compute=dp.get_precision('Account'),
    )
    revenue_this_year = fields.Float(
        string='Revenue_Actual_(this_year)',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_planned = fields.Float(
        string='Total_Budget_Planned',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_expense = fields.Float(
        string='Total_Expense',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_commit = fields.Float(
        string='Total_Commitment',
        digits_compute=dp.get_precision('Account'),
    )
    total_budget_balance = fields.Float(
        string='Total_Balance',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_current = fields.Float(
        string='Yearly_Budget_Current',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_release = fields.Float(
        string='Yearly_Budget_Release',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_commit = fields.Float(
        string='Yearly_Commitment',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_expense = fields.Float(
        string='Yearly_Expense',
        digits_compute=dp.get_precision('Account'),
    )
    yearly_budget_balance = fields.Float(
        string='Yearly_Balance',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q1 = fields.Float(
        string='FY1/Q1',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q2 = fields.Float(
        string='FY1/Q2',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1_q3 = fields.Float(
        string='FY1/Q3',
        digits_compute=dp.get_precision('Account'),
    )
    amount_year1_q4 = fields.Float(
        string='FY1/Q4',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy1 = fields.Float(
        string='FY1',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy2 = fields.Float(
        string='FY2',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy3 = fields.Float(
        string='FY3',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy4 = fields.Float(
        string='FY4',
        digits_compute=dp.get_precision('Account'),
    )
    amount_fy5 = fields.Float(
        string='FY5',
        digits_compute=dp.get_precision('Account'),
    )
    amount_total = fields.Float(
        string='Amount_Total',
        digits_compute=dp.get_precision('Account'),
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
