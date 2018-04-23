# -*- coding: utf-8 -*-
from openerp import models, api, _


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.model
    def create_project(self, data_dict):
        """ Create project using friendly dict
        data_dict = {
            'code': 'XXX', 'name': 'YYY', ...
            'budget_plan_ids': [{'fiscalyear_id': '2018',
                                 'activity_gorup_id': 'AG001', ...},
                                {'fiscalyear_id': '2019',
                                 'activity_gorup_id': 'AG002', ...}],
        }
        """
        try:
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            if res['is_success']:
                res_id = res['result']['id']
                document = self.browse(res_id)
                # Refresh
                document.refresh_budget_line(data_dict)
                document.prepare_fiscal_plan_line(data_dict, force_run=True)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res

    @api.model
    def update_project(self, data_dict):
        """ Friendly update data, sample data_dict,
        data_dict = {
            'code': 'XXX', 'pm_employee_id': '102190',
            'budget_plan_ids': [{'fiscalyear_id': '2018',
                                 'activity_group_id': 'AG0001',
                                 'm1': 102020.00, 'm3': 929201.00}]
        }
        Note:
         - Record updated using project 'code' as search key
         - Record fields will be updated if in the dict
         - Record one2many fields will be deleted then created
        """
        try:
            # Update project, use 'code' as search key
            res = self.env['pabi.utils.ws'].\
                friendly_update_data(self._name, data_dict, 'code')
            if res['is_success']:
                res_id = res['result']['id']
                document = self.browse(res_id)
                # Refresh
                document.refresh_budget_line(data_dict)
                document.prepare_fiscal_plan_line(data_dict, force_run=True)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': e,
            }
            self._cr.rollback()
        return res

    @api.model
    def get_all_fy_budget_release(self, project_code):
        """ Return result as dict i.e., {'2018': 234, '2019': 456} """
        res = {
            'is_success': False,
            'result': False,
            'messages': False,
        }
        project = self.name_search(project_code, operator='=')
        if len(project) != 1:
            res['messages'] = [_('%s not found!') % project_code]
        else:
            result = {}
            p = self.browse(project[0][0])
            for l in p.summary_expense_ids:
                result[l.fiscalyear_id.name] = l.released_amount
            res['is_success'] = True
            res['result'] = result
        return res

    @api.model
    def get_current_fy_budget_release(self, project_code):
        """ Return result as float """
        res = self.get_all_fy_budget_release(project_code)
        if res['is_success']:
            fiscalyear_id = self.env['account.fiscalyear'].find()
            fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
            result = res['result'] or {}
            res['result'] = result.get(fiscal.name, 0.0)
        return res
