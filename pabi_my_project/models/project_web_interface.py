# -*- coding: utf-8 -*-
import logging
from openerp import models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_is_zero

_logger = logging.getLogger(__name__)

CLOSE_PROJECT = ['ยุติโครงการ', 'ปิดโครงการแบบมีเงื่อนไข', 'ปิดโครงการโดยสมบูรณ์']


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.model
    def create_project(self, data_dict):
        _logger.info('create_project(), input: %s' % data_dict)
        """ Create project using friendly dict
        data_dict = {
            'code': 'K-00-00006',
            'name': '[K-00-00006]',
            'org_id': 'MTEC',
            'project_group_id': 'TAIST-Tokyo Tech scholarship',
            'date_start': '2018-01-01',
            'date_approve': '2018-01-01',
            'date_end': '2020-06-01',
            'pm_employee_id': '004010',
            'pm_section_id': '105015',
            'analyst_employee_id': '004010',
            'analyst_section_id': '105015',

            'budget_plan_expense_ids': [
                {
                    'fiscalyear_id': '2018',
                    'budget_method': 'expense',
                    'charge_type': 'external',
                    'activity_group_id': 'AG0001',
                    'm1': 10000.00,
                    'm2': 10000.00,
                    'm3': 10000.00,
                    'm4': 10000.00,
                    'm5': 10000.00,
                    'm6': 10000.00,
                    'm7': 10000.00,
                    'm8': 10000.00,
                    'm9': 10000.00,
                    'm10': 10000.00,
                    'm11': 10000.00,
                    'm12': 10000.00,
                },
                {
                    'fiscalyear_id': '2019',
                    'budget_method': 'expense',
                    'charge_type': 'external',
                    'activity_group_id': 'AG0002',
                    'm1': 10000.00,
                    'm2': 10000.00,
                    'm3': 10000.00,
                    'm4': 10000.00,
                    'm5': 10000.00,
                    'm6': 10000.00,
                    'm7': 10000.00,
                    'm8': 10000.00,
                    'm9': 10000.00,
                    'm10': 10000.00,
                    'm11': 10000.00,
                    'm12': 10000.00,
                },
            ],
        }
        """
        try:
            res = self.env['pabi.utils.ws'].friendly_create_data(self._name,
                                                                 data_dict)
            if res['is_success']:
                res_id = res['result']['id']
                project = self.browse(res_id)
                # Refresh
                project.refresh_budget_line(data_dict)
                project.prepare_fiscal_plan_line(data_dict, force_run=True)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('create_project(), output: %s' % res)
        return res

    def update_project_function(self, data_dict):
        _logger.info('update_project(), input: %s' % data_dict)
        """
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
                if 'budget_plan_expense_ids' not in data_dict and \
                   'budget_plan_revenue_ids' not in data_dict and \
                   'budget_plan_ids' not in data_dict:
                    return res
                project = self.browse(res_id)  # Project
                # Release with latest release history (if any)
                if res_id:
                    self._cr.execute("""
                        select max(id)
                        from res_project_budget_release
                        where project_id = %s
                        group by fiscalyear_id
                    """, (res_id, ))
                    Release = self.env['res.project.budget.release']
                    rels = \
                        Release.browse([x[0] for x in self._cr.fetchall()])
                    for rec in rels:
                        project.with_context(ignore_lock_release=True,
                                             ignore_current_fy_lock=True).\
                            _release_fiscal_budget(rec.fiscalyear_id,
                                                   rec.released_amount)
                # Refresh
                project.refresh_budget_line(data_dict)
                project.prepare_fiscal_plan_line(data_dict, force_run=True)
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('update_project(), output: %s' % res)
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
        Steps:
            - Check function check_budget_commit_asset_owner before
            - if return check_budget_commit and check_asset_owner is False,
            it update project.
        """
        res = {
            'is_success': False,
            'result': False,
            'messages': _('budget_commit or asset_owner are False'),
        }
        if data_dict['project_status'].encode('utf8') in CLOSE_PROJECT:
            res = self.check_budget_commit_asset_owner(data_dict)
            if res['is_success'] and not (
                    res['check_budget_commit'] or res['check_asset_owner']
            ):
                res = self.update_project_function(data_dict)
        else:
            res = self.update_project_function(data_dict)
        return res

    @api.model
    def get_all_fy_budget_release(self, project_code):
        _logger.info('get_all_fy_budget_release(), input: %s' % project_code)
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
        _logger.info('get_all_fy_budget_release(), output: %s' % res)
        return res

    @api.model
    def get_current_fy_budget_release(self, project_code):
        _logger.info('get_current_fy_budget_release(), input: %s' %
                     project_code)
        """ Return result as float """
        res = self.get_all_fy_budget_release(project_code)
        if res['is_success']:
            fiscalyear_id = self.env['account.fiscalyear'].find()
            fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
            result = res['result'] or {}
            res['result'] = result.get(fiscal.name, 0.0)
        _logger.info('get_current_fy_budget_release(), output: %s' % res)
        return res

    @api.model
    def check_budget_commit_asset_owner(self, data_dict):
        """ Example Test :
        data_dict = {
            'project_code': 'P1300475'
        }
        """
        _logger.info(
            'check_budget_commit_asset_owner(), input: %s' % data_dict)
        if data_dict.get('project_code', False):
            data_dict['code'] = data_dict.pop('project_code')
        try:
            # Update project, use 'code' as search key
            res = self.env['pabi.utils.ws'].\
                friendly_update_data(self._name, data_dict, 'code')
            if res.get('is_success', False):
                res['check_budget_commit'] = False
                res['check_asset_owner'] = False
                res_id = res['result']['id']
                project_id = self.browse(res_id)
                if project_id:
                    self._cr.execute("""
                        select COALESCE(sum(amount_pr_commit),0) +
                        COALESCE(sum(amount_po_commit),0) +
                        COALESCE(sum(amount_exp_commit),0) as amount_total
                        from budget_consume_report
                        where project_id = %s and budget_method = 'expense'
                        and charge_type = 'external'
                    """ % (project_id.id))
                    amount_total = \
                        self._cr.dictfetchone()['amount_total']
                    # Check commit in project
                    if not float_is_zero(amount_total, precision_rounding=5):
                        res['check_budget_commit'] = True

                asset = self.env['account.asset'].search([
                    ('owner_project_id', '=', res_id)])
                if asset:
                    res['check_asset_owner'] = True
                res['messages'] = [_('Check Budget Commit and Asset Owner')]
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
        self._cr.rollback()
        _logger.info('check_budget_commit_asset_owner(), output: %s' % res)
        return res

    @api.model
    def change_project_budget_lock_status(self, project_code, status):
        _logger.info('change_project_budget_lock_status(), input: [%s, %s]' %
                     (project_code, status))
        """ Update lock status,
        state = ['lock', 'unlock']
        """
        res = {
            'is_success': False,
            'result': False,
            'messages': False,
        }
        try:
            if status not in ('lock', 'unlock'):
                raise ValidationError(_('Wrong input status: %s') % status)
            project_id = self.name_search(project_code, operator='=')
            if len(project_id) > 1:
                raise ValidationError(
                    _('%s match more > 1 record.') % project_code)
            elif len(project_id) == 0:
                raise ValidationError(
                    _('%s found no match.') % project_code)
            project = self.browse(project_id[0][0])
            project.write({'lock_release': status == 'lock' and True or False})
            res['is_success'] = True
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('change_project_budget_lock_status(), output: %s' % res)
        return res


class ResProjectBudgetPlan(models.Model):
    _inherit = 'res.project.budget.plan'

    @api.model
    def release_budget(self, plan_id, amount):
        """ Helper function for webservice call """
        budget_line = self.search([('id', '=', plan_id)])
        if float_compare(amount, budget_line.planned_amount, 2) == 1:
            raise ValidationError(
                _('Release amount exceed planned amount!'))
        budget_line.write({'released_amount': amount})
        budget_line.project_id._trigger_auto_sync()
        return True
