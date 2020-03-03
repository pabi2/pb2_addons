# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


@job
def action_recurring_create_entries(session, model_name, res_id):
    try:
        session.pool[model_name].create_entries(
            session.cr, session.uid, [res_id], session.context
        )
        entry = session.pool[model_name].browse(
            session.cr, session.uid, res_id
        )
        return {'move_ids': entry.move_ids.ids}
    except Exception as e:
        raise RetryableJobError(e)


class AccountUseModel(models.TransientModel):
    _inherit = 'account.use.model'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )

    @api.multi
    def create_entries(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(AccountUseModel, self).create_entries()
        # Enqueue
        if self.async_process:
            active_id = self._context.get('active_id')
            account_model = self.env['account.model'].browse(active_id)
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Generate Entries - %s' % account_model.name
            uuid = action_recurring_create_entries.delay(
                session, self._name, self.id, description=description
            )
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref(
                'pabi_async_process.recurring_create_entrie'
            )
        else:
            return super(AccountUseModel, self).create_entries()
