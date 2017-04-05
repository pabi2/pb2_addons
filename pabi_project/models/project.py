# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _rec_name = 'number'

    number = fields.Char(
        string='Project Number',
        readonly=True,
        default='/',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Project Manager Section',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Project Manager Org',
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Core Mission',
    )
    amount_budget = fields.Float(
        string='Budget',
        default=0.0,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Source of Fund',
        # readonly=True,
        default=lambda self: self.env.ref('base.fund_nstda'),
    )
    month_duration = fields.Integer(
        string='Duration (months)',
    )
    operation_area = fields.Char(
        string='Operation Area',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    approval_info = fields.Text(
        string='Approval info',
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

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].\
                next_by_code('project.project')
        return super(ProjectProject, self).create(vals)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        employee = self.user_id.employee_id
        employee = self.user_id.partner_id.employee_id
        self.section_id = employee.section_id
        self.org_id = employee.org_id

    @api.onchange('month_duration', 'date_start')
    def _onchange_date(self):
        date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
        date_end = date_start + relativedelta(months=self.month_duration)
        self.date = date_end.strftime('%Y-%m-%d')


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _rec_name = 'number'

    number = fields.Char(
        string='Task Number',
        readonly=True,
        default='/',
    )
    amount_budget = fields.Float(
        string='Phase Budget',
        default=0.0,
    )
    month_duration = fields.Integer(
        string='Duration (months)',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    contract_number = fields.Char(
        string='Phase Contract No.'
    )
    date_contract_start = fields.Date(
        string='Phase Contract Start Date',
    )
    contract_day_duration = fields.Integer(
        string='Phase Contract Duration (days)',
    )

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            prefix = 'N/A-'
            if vals.get('project_id', False):
                project = \
                    self.env['project.project'].browse(vals.get('project_id'))
                prefix = project.number + '-'
            vals['number'] = prefix + '{:02d}'.format(vals.get('sequence', 0))
        return super(ProjectTask, self).create(vals)

    @api.onchange('month_duration', 'date_start')
    def _onchange_date(self):
        date_start = datetime.strptime(self.date_start,
                                       '%Y-%m-%d  %H:%M:%S').date()
        date_end = date_start + relativedelta(months=self.month_duration)
        self.date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')
