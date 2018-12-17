# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import RedirectWarning
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


def related_asset(session, thejob):
    asset_id = thejob.args[1]
    action = {
        'name': _("Asset"),
        'type': 'ir.actions.act_window',
        'res_model': "account.asset",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': asset_id,
    }
    return action


@job
@related_action(action=related_asset)
def action_compute_depreciation_board(session, model_name, res_id):
    try:
        session.pool[model_name].\
            compute_depreciation_board(session.cr, session.uid,
                                       [res_id], session.context)
        asset = session.pool[model_name].browse(session.cr,
                                                session.uid, res_id)
        return {'asset_id': asset.id}
    except Exception, e:
        raise RetryableJobError(e)


class AccountAsset(PabiAsync, models.Model):
    _inherit = 'account.asset'

    async_process = fields.Boolean(
        string='Run task in background?',
        default=True,
        help="This will run compute asset depreciation in back ground",
    )
    job_id = fields.Many2one(
        'queue.job',
        string='Job',
        compute='_compute_job_uuid',
    )
    uuid = fields.Char(
        string='Job UUID',
        compute='_compute_job_uuid',
    )

    @api.multi
    def _compute_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_compute_depreciation_board', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.job_id = jobs and jobs[0] or False
            rec.uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(AccountAsset, self).compute_depreciation_board()
        # Enqueue
        if self.async_process:
            if self.job_id:
                message = _('Compute asset depreciation job is still running!')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s  - Asset Depreciation Job' % self.name
            uuid = action_compute_depreciation_board.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'asset_compute_depreciation_board')
            return True
        else:
            return super(AccountAsset, self).compute_depreciation_board()
