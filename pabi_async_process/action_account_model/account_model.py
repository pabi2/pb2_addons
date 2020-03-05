# -*- coding: utf-8 -*-
from openerp import models, api, fields, exceptions, _
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


def related_view_account_move(session, thejob):
    try:
        job = session.env['queue.job'].search([('uuid', '=', thejob._uuid)])
        job_dict = eval(job.result)
        action = {
            'domain': job_dict['domain'],
            'name': job_dict['name'],
            'view_type': job_dict['view_type'],
            'view_mode': job_dict['view_mode'],
            'res_model': job_dict['res_model'],
            'type': job_dict['type'],
        }
        return action
    except:
        raise exceptions.Warning(_('No action available for this job'))


@job
@related_action(action=related_view_account_move)
def action_recurring_create_entries(session, model_name, res_id, context=False):
    try:
        res = session.pool[model_name].create_entries(
            session.cr, session.uid, [res_id], session.context
        )
        return res
    except Exception, e:
        raise RetryableJobError(e)


class AccountUseModel(models.TransientModel):
    _inherit = 'account.use.model'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=False,
    )
    get_context = fields.Char()

    @api.multi
    def _save_context(self):
        self.get_context = self._context

    @api.multi
    def create_entries(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            ctx = eval(self.get_context)
            self = self.with_context(ctx)
            return super(AccountUseModel, self).create_entries()
        # Enqueue
        if self.async_process:
            active_id = self._context.get('active_id')
            account_model = self.env['account.model'].browse(active_id)
            self._save_context()
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
