# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from ..models.common import PabiAsync
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_generate_entries(session, thejob):
    generate_id = thejob.args[1]
    action = {
        'name': _('Generate Entries'),
        'type': 'ir.actions.act_window',
        'res_model': 'account.subscription.generate',
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': generate_id,
    }
    return action


@job
@related_action(action=related_generate_entries)
def action_generate_recurring_entries(session, model_name, res_id):
    try:
        session.pool[model_name].action_generate(session.cr, session.uid,
                                                 [res_id], session.context)
        entry = session.pool[model_name].browse(session.cr, session.uid,
                                                res_id)
        return {'move_ids': entry.move_ids.ids}
    except Exception, e:
        raise FailedJobError(e)


class AccountSubscriptionGenerate(PabiAsync, models.Model):
    _inherit = 'account.subscription.generate'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
            description = 'Generate Entries - %s - %s' % (period, model_types)
            uuid = action_generate_recurring_entries.delay(
                session, self._name, self.id, description=description)
            # Checking for running task, use the same signature as delay()
            task_name = "%s('%s', %s)" % ('action_generate_recurring_entries',
                                          self._name, self.id)
            self._check_queue(task_name, desc=description,
                              type='always', uuid=uuid)
        else:
            return super(AccountSubscriptionGenerate, self).action_generate()
