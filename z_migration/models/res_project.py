# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning as UserError
# import os
# import csv


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.multi
    def mork_release_budget(self, data):
        self.ensure_one()
        # Make sure project code only one
        project = self.search([('code', '=', self.code)])
        if len(project) > 1:
            raise UserError(_('Duplicate project code'))

        # Get project budget summary of current fiscal year
        fiscalyear_id = self.env['account.fiscalyear'].find()
        project_budget_summary = self.summary_expense_ids.filtered(
            lambda l: l.fiscalyear_id.id == fiscalyear_id)
        if len(project_budget_summary) > 1:
            raise UserError(_('Duplicate fiscal year'))

        # Create project budget release wizard
        Wizard = self.env['res.project.budget.release']
        # path = '%s/data/my_project_release_budget.csv' % \
        #     os.path.realpath(__file__).replace('/models/res_project.py', '')
        # reader = csv.reader(open(path))
        # data = filter(lambda l: l[0] == self.code, reader)
        if not data:
            raise UserError(_('No project code in data file csv'))
        elif len(data) > 1:
            raise UserError(_('Duplicate project code in data file csv'))
        prepare_wizard = {
            'project_id': project_budget_summary.project_id.id,
            'fiscalyear_id': project_budget_summary.fiscalyear_id.id,
            'released_amount': data[0][1],
            'user_id': self.env.user.id,
        }
        Wizard.create(prepare_wizard)
        return True
