# -*- coding: utf-8 -*-
import ast

from openerp import models, api, fields
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


@job
def action_generate_recurring_entries(session, calendar_period_id,
                                      model_type_ids):
    try:
        # Mock account.subscription.generate object
        period = session.pool['account.period'].browse(session.cr, session.uid,
                                                       calendar_period_id)
        vals = {'date': period.date_stop,
                'calendar_period_id': calendar_period_id,
                'model_type_ids': [(6, 0, model_type_ids)]}
        Generate = session.pool['account.subscription.generate']
        _id = Generate.create(session.cr, session.uid, vals)
        res = Generate.action_generate(session.cr, session.uid,
                                       [_id], session.context)
        domain = ast.literal_eval(res['domain'])
        return {'move_ids': domain[0][2]}
    except Exception, e:
        raise FailedJobError(e)


class AccountSubscriptionGenerate(PabiAsync, models.TransientModel):
    _inherit = 'account.subscription.generate'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )

    @api.multi
    def action_generate(self):
        if self._context.get('job_uuid', False):  # Called from @job
            return super(AccountSubscriptionGenerate, self).action_generate()
        # Enqueue
        if self.async_process:
            session = ConnectorSession(self._cr, self._uid, self._context)
            period = self.calendar_period_id.calendar_name
            model_types = ', '.join([x.name for x in self.model_type_ids])
            description = 'Generate Entrie - %s - %s' % (period, model_types)
            action_generate_recurring_entries.delay(
                session, self.calendar_period_id.id,
                self.model_type_ids.ids, description=description)
            # Checking for running task, use the same signature as delay()
            task_name = "%s(%s, %s)" % ('action_generate_recurring_entries',
                                        self.calendar_period_id.id,
                                        self.model_type_ids.ids)
            self._check_queue(task_name, desc=description, type='mytask')
        else:
            return super(AccountSubscriptionGenerate, self).action_generate()
