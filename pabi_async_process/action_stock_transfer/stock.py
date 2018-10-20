# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import RedirectWarning, ValidationError
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_stock_picking(session, thejob):
    picking_id = thejob.args[1]
    action = {
        'name': _("Transfer"),
        'type': 'ir.actions.act_window',
        'res_model': "stock.picking",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': picking_id,
    }
    return action


@job
@related_action(action=related_stock_picking)
def action_do_transfer(session, model_name, res_id):
    try:
        session.pool[model_name].do_transfer(session.cr, session.uid,
                                             [res_id], session.context)
        picking = session.pool[model_name].browse(session.cr,
                                                  session.uid, res_id)
        return {'picking_id': picking.id}
    except Exception, e:
        raise FailedJobError(e)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    async_process = fields.Boolean(
        string='Do transfer in background?',
        default=False,
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
                ('action_do_transfer', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.job_id = jobs and jobs[0] or False
            rec.uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def do_transfer(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(StockPicking, self).do_transfer()
        # Enqueue
        if self.async_process:
            if self.job_id:
                message = _('Do Transfer(s)')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Do Transfer(s)' % self.name
            uuid = action_do_transfer.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'stock_transfer')
        else:
            return super(StockPicking, self).do_transfer()

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        print uid
        pick_obj = self.browse(cr, uid, picking)
        if pick_obj.async_process and pick_obj.job_id:
            raise ValidationError(_('Transfer job is running.\n'
                                    'Please come back to check later.'))
        return super(StockPicking, self).\
            do_enter_transfer_details(cr, uid, picking, context=context)
