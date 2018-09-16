# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.pabi_chartfield.models.chartfield import CHART_VIEW_LIST


@job
def action_generate_budget_plan(session, model_name, res_id):
    try:
        session.pool[model_name].action_generate_budget_plan(
            session.cr, session.uid, [res_id], session.context)
        return _("Budget Plan created successfully")
    except Exception as e:
        raise FailedJobError(e)


class GenerateBudgetPlan(PabiAsync, models.TransientModel):
    _inherit = 'generate.budget.plan'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )

    @api.multi
    def action_generate_budget_plan(self):
        if self._context.get('job_uuid', False):  # Called from @job
            return \
                super(GenerateBudgetPlan, self).action_generate_budget_plan()
        # Enqueue
        if self.async_process:
            session = ConnectorSession(self._cr, self._uid, self._context)
            chart_view = dict(CHART_VIEW_LIST).get(self.chart_view, False)
            fiscalyear = self.fiscalyear_id.name
            description = 'Generate Budget Plans - %s - %s' \
                % (chart_view, fiscalyear)
            uuid = action_generate_budget_plan.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'generate_budget_plan')
            # Checking for running task, use the same signature as delay()
            task_name = "%s('%s', %s)" % ('action_generate_budget_plan',
                                          self._name, self.id)
            self._check_queue(task_name, desc=description, type='always')
        else:
            return \
                super(GenerateBudgetPlan, self).action_generate_budget_plan()
