# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug.utils


class ExternalFundRuleURL(http.Controller):
    """
    - http://localhost:8069/fund_rule?mode=create&project=P1350398
    - http://localhost:8069/fund_rule?mode=edit&project=P1350045&fund=100012
    - http://localhost:8069/fund_rule?mode=list&project=P1350398
    """
    @http.route('/fund_rule/', type='http', auth='public')
    def myproject_to_project(self, **kw):
        mode = kw.get('mode', False)
        if mode == 'edit':
            project = kw.get('project', False)
            fund = kw.get('fund', False)
            return self._fund_rule_edit_url(project, fund)
        elif mode == 'create':
            project = kw.get('project', False)
            return self._fund_rule_create_url(project)
        elif mode == 'list':
            project = kw.get('project', False)
            return self._fund_rule_list_url(project)

    def _fund_rule_edit_url(self, project, fund):
        Fund = request.registry.get('res.fund')
        FundRule = request.registry.get('budget.fund.rule')
        Project = request.registry.get('res.project')
        fids = Fund.name_search(request.cr, SUPERUSER_ID,
                                fund, operator='=')
        pids = Project.name_search(request.cr, SUPERUSER_ID,
                                   project, operator='=')
        if len(fids) != 1 or len(pids) != 1:
            return False
        fund_id = fids[0][0]
        project_id = pids[0][0]
        frs = FundRule.search(request.cr, SUPERUSER_ID,
                              [('fund_id', '=', fund_id),
                               ('project_id', '=', project_id),
                               ('state', '!=', 'cancel')])
        if len(frs) != 1:
            return False
        fund_rule = FundRule.browse(request.cr, SUPERUSER_ID, frs[0])
        # action
        Action = request.registry.get('ir.model.data')
        action_id = Action.search(
            request.cr, SUPERUSER_ID,
            [('module', '=', 'pabi_budget_fund_rule'),
             ('name', '=', 'action_budget_fund_rule')])
        action = Action.browse(request.cr, SUPERUSER_ID, action_id)
        # URL
        url = "/web?toolbar=hide&#model=budget.fund.rule&view_type=form"
        ext_url = "&id=%s&action=%s" % (fund_rule.id, action.res_id)
        return werkzeug.utils.redirect(url + ext_url)

    def _fund_rule_create_url(self, project):
        Project = request.registry.get('res.project')
        pids = Project.name_search(request.cr, SUPERUSER_ID,
                                   project, operator='=')
        if len(pids) != 1:
            return False
        project_id = pids[0][0]
        # action
        Action = request.registry.get('ir.model.data')
        WindowAction = request.registry.get('ir.actions.act_window')
        action_id = Action.search(
            request.cr, SUPERUSER_ID,
            [('module', '=', 'pabi_budget_fund_rule'),
             ('name', '=', 'action_new_budget_fund_rule')])
        action = Action.browse(request.cr, SUPERUSER_ID, action_id)
        ctx = "{'default_project_id': %s}" % project_id
        WindowAction.write(request.cr, SUPERUSER_ID,
                           [action.res_id], {'context': ctx})
        # URL
        url = "/web?toolbar=hide&#model=budget.fund.rule&view_type=form"
        ext_url = "&action=%s" % (action.res_id,)
        return werkzeug.utils.redirect(url + ext_url)

    def _fund_rule_list_url(self, project):
        Project = request.registry.get('res.project')
        pids = Project.name_search(request.cr, SUPERUSER_ID,
                                   project, operator='=')
        if len(pids) != 1:
            return False
        project_id = pids[0][0]
        # action
        Action = request.registry.get('ir.model.data')
        WindowAction = request.registry.get('ir.actions.act_window')
        action_id = Action.search(
            request.cr, SUPERUSER_ID,
            [('module', '=', 'pabi_budget_fund_rule'),
             ('name', '=', 'action_budget_fund_rule')])
        action = Action.browse(request.cr, SUPERUSER_ID, action_id)
        WindowAction.write(request.cr, SUPERUSER_ID, [action.res_id],
                           {'domain':
                            "[('project_id', '=', %s)]" % project_id})
        # URL
        url = "/web?toolbar=hide&#model=budget.fund.rule&view_type=tree"
        ext_url = "&action=%s" % (action.res_id,)
        return werkzeug.utils.redirect(url + ext_url)
