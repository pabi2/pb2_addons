# -*- coding: utf-8 -*-
from openerp import models, api


ACTION = {
    'res.invest.construction':
        'pabi_invest_construction.action_invest_construction',
    'res.invest.construction.phase':
        'pabi_invest_construction.action_invest_construction_phase',
}


def common_confirm_approve(self):
    context = self._context.copy()
    active_ids = context.get('active_ids', [])
    active_model = context.get('active_model', False)
    fail_result_ids = []
    for rec in self.env[active_model].browse(active_ids):
        try:
            if rec.state != 'draft':
                continue
            # Submit
            rec.action_submit()
            # Approve
            rec.action_approve()
        except Exception:
            fail_result_ids.append(rec.id)

    action = self.env.ref(
        'pabi__actions.action_auto_approve_invest_construction_result_wizard')
    result = action.read()[0]
    context = {
        'result': not fail_result_ids and 'pass' or 'fail',
        'fail_result_ids': fail_result_ids,
        'active_action': ACTION.get(active_model, False),
    }
    result.update({'context': context})
    return result


class AutoApproveInvestConstructionWizard(models.TransientModel):
    _name = 'auto.approve.invest.construction.wizard'

    @api.multi
    def confirm_approve(self):
        self.ensure_one()
        return common_confirm_approve(self)


class AutoApproveInvestConstructionResultWizard(models.TransientModel):
    _name = 'auto.approve.invest.construction.result.wizard'

    @api.multi
    def execute(self):
        self.ensure_one()
        context = self._context.copy()
        fail_result_ids = context.get('fail_result_ids', [])
        active_action = context.get('active_action', False)

        if not active_action:
            return True

        action = self.env.ref(active_action)
        result = action.read()[0]
        result.update({'domain': [('id', 'in', fail_result_ids)]})
        return result
