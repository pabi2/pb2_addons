# -*- coding: utf-8 -*-
from openerp import api, fields, models, _


class InvestConstructionProjectPlanWizard(models.TransientModel):
    _name = 'invest.construction.project.plan.wizard'

    invest_construction_ids = fields.Many2many(
        'res.invest.construction',
        'construction_project_plan_wizard_rel',
        'wizard_id', 'invest_construction_id',
        string='Project (C)',
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'fiscalyear_project_plan_wizard_rel',
        'wizard_id', 'fiscalyear_id',
        string='Fiscal Year(s)',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('unapprove', 'Un-Approved'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('delete', 'Deleted'),
         ('cancel', 'Cancelled'),
         ('close', 'Closed'),
         ],
        string='Status',
        default='approve',
    )

    @api.multi
    def open_report(self):
        self.ensure_one()
        action = self.env.ref('pabi_invest_construction.'
                              'action_invest_construction_budget_plan')
        result = action.read()[0]
        # Get filter
        domain = []
        if self.invest_construction_ids:
            domain += [('invest_construction_id', 'in',
                        self.invest_construction_ids.ids)]
        if self.fiscalyear_ids:
            domain += [('fiscalyear_id', 'in',
                        self.fiscalyear_ids.ids)]
        if self.state:
            domain += [('invest_construction_id.state', '=', self.state)]

        result.update({'domain': domain})
        return result


class InvestConstructionPhasePlanWizard(models.TransientModel):
    _name = 'invest.construction.phase.plan.wizard'

    invest_construction_ids = fields.Many2many(
        'res.invest.construction',
        'construction_phase_plan_wizard_rel',
        'wizard_id', 'invest_construction_id',
        string='Project (C)',
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'fiscalyear_project_plan_wizard_rel',
        'wizard_id', 'fiscalyear_id',
        string='Fiscal Year(s)',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('unapprove', 'Un-Approved'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('delete', 'Deleted'),
         ('cancel', 'Cancelled'),
         ('close', 'Closed'),
         ],
        string='Status',
        default='approve',
    )

    @api.multi
    def open_report(self):
        self.ensure_one()
        action = self.env.ref('pabi_invest_construction.'
                              'action_invest_construction_phase_plan')
        result = action.read()[0]
        # Get filter
        domain = []
        if self.invest_construction_ids:
            domain += [('invest_construction_id', 'in',
                        self.invest_construction_ids.ids)]
        if self.fiscalyear_ids:
            domain += [('fiscalyear_id', 'in',
                        self.fiscalyear_ids.ids)]
        if self.state:
            domain += [('invest_construction_id.state', '=', self.state)]

        result.update({'domain': domain})
        return result
