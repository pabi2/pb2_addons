# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBudgetPrepare(models.Model):
    _name = "account.budget.prepare"
    _description = "Budget Prepare"

    name = fields.Char(
        string='Name',
        required=True,
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=fields.Date.today(),
    )
    date_submit = fields.Date(
        string='Submitted Date',
        copy=False,
        readonly=True,
    )
    date_approve = fields.Date(
        string='Approved Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
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
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        required='True',
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        compute='_compute_all',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        compute='_compute_all',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('cancel', 'Cancelled'),
         ('reject', 'Rejected'),
         ('approve', 'Approved')],
        string='Status',
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
    )
    project_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Budget Prepare Lines',
        copy=True,
    )
    performance_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Budget Prepare Lines',
        copy=True,
    )
    budget_line_ids = fields.One2many(
        'account.budget.prepare.line',
        'prepare_id',
        string='Budget Prepare Lines',
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('account.budget'),
    )
    amount_budget_request = fields.Float(
        string='Budget Request',
    )
    amount_budget_policy = fields.Float(
        string='Budget Policy',
    )
    amount_budget_release = fields.Float(
        string='Budget Release',
    )
    input_file = fields.Binary(
        string='Import myProject (.xlsx)',
    )

    @api.multi
    @api.depends('program_id')
    def _compute_all(self):
        for rec in self:
            rec.program_group_id = rec.program_id.program_group_id
            rec.functional_area_id = rec.program_group_id.functional_area_id

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def budget_submit(self):
        self.write({
            'state': 'submit',
            'date_submit': fields.Date.today(),
        })
        return True

    @api.multi
    def budget_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def budget_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def budget_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def budget_approve(self):
        self.write({
            'state': 'approve',
            'validating_user_id': self._uid,
            'date_approve': fields.Date.today(),
        })
        return True


class AccountBudgetPrepareLine(models.Model):

    _name = "account.budget.prepare.line"
    _description = "Budget Line"

    c_or_n = fields.Selection(
        [('continue', 'Continue'),
         ('new', 'New')],
        string='C/N',
        default='new',
    )
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
    # Project Structure
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        compute='_compute_all',
        store=True,  # Follow header
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        compute='_compute_all',
        store=True,  # Follow header
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        compute='_compute_all',
        store=True,  # Follow header
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
    )
    project_kind = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non-Research')],
        string='Research / Non-Research',
    )
    project_objective = fields.Char(
        string='Objective',
    )
    project_type = fields.Char(
        string='Project Type',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    # Project Info (myProject)
    manager_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
    )
    date_from = fields.Date(
        string='Start Date',
    )
    date_to = fields.Date(
        string='End Date',
    )
    project_duration = fields.Integer(
        string='Duration',
    )
    project_status = fields.Char(
        string='Project Status',
    )
    analyst_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Analyst',
    )
    ref_program_id = fields.Many2one(
        'res.program',
        string='Program Reference',
    )
    external_fund_type = fields.Selection(
        [('government', 'Government'),
         ('private', 'Private Organization'),
         ('oversea', 'Oversea')],
        string='External Fund Type',
    )
    external_fund_name = fields.Char(
        string='External Fund Name',
    )
    priority = fields.Char(
        string='Priority',
    )
    # Project Performance (myPerformance)
    pfm_publications = fields.Integer(
        string='Publication',
    )
    pfm_patents = fields.Integer(
        string='Patent',
    )
    pfm_petty_patents = fields.Integer(
        string='Petty Patent',
    )
    pfm_copyrights = fields.Integer(
        string='Copy Right',
    )
    pfm_trademarks = fields.Integer(
        string='Trademark',
    )
    pfm_plant_varieties = fields.Integer(
        string='Plant Varieties',
    )
    pfm_laboratory_prototypes = fields.Integer(
        string='Laboratory Prototype',
    )
    pfm_field_prototypes = fields.Integer(
        string='Field Prototype',
    )
    pfm_commercial_prototypes = fields.Integer(
        string='Commercial Prototype',
    )
    pfm_revenue_budget = fields.Float(
        string='Revenue Budget',
    )
    pfm_revenue_overall_plan = fields.Float(
        string='Overall Revenue Plan',
    )
    pfm_revenue_accum = fields.Float(
        string='Accum. Revenue',
    )
    pfm_revenue_current_year = fields.Float(
        string='Current Year Revenue',
    )
    pfm_expense_overall_budget = fields.Float(
        string='Overall Expense Budget',
    )
    pfm_expense_accum = fields.Float(
        string='Accum. Expense',
    )
    pfm_commitment_accum = fields.Float(
        string='Accum. Commitment',
    )
    pfm_expense_remaining_budget = fields.Float(
        string='Remaining Expense Budget',
    )
    # Budget Control
    cur_current_budget = fields.Float(
        string='Current Budget',
    )
    cur_release_budget = fields.Float(
        string='Release Budget',
    )
    cur_commit_budget = fields.Float(
        string='Commit Budget',
    )
    cur_actual = fields.Float(
        string='Actual',
    )
    cur_remaining_budget = fields.Float(
        string='Remaining Budget',
    )
    cur_estimated_commitment = fields.Float(
        string='Estimated Commitment',
    )
    fy1q1 = fields.Float(
        string='FY1/Q1',
    )
    fy1q2 = fields.Float(
        string='FY1/Q2',
    )
    fy1q3 = fields.Float(
        string='FY1/Q3',
    )
    fy1q4 = fields.Float(
        string='FY1/Q4',
    )
    fy1 = fields.Float(
        string='FY1',
    )
    fy2 = fields.Float(
        string='FY2',
    )
    fy3 = fields.Float(
        string='FY3',
    )
    fy4 = fields.Float(
        string='FY4',
    )
    fy5 = fields.Float(
        string='FY5',
    )
    total = fields.Float(
        string='Total',
    )

    @api.multi
    @api.depends('prepare_id.program_id')
    def _compute_all(self):
        for rec in self:
            # Default for functional area and program group
            rec.program_id = rec.prepare_id.program_id
            rec.program_group_id = rec.program_id.program_group_id
            rec.functional_area_id = rec.program_group_id.functional_area_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
