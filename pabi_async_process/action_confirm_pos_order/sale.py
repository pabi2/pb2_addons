# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError


def related_pos_sale_order(session, thejob):
    order_id = thejob.args[1]
    action = {
        'name': _("POS Order"),
        'type': 'ir.actions.act_window',
        'res_model': "sale.order",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': order_id,
    }
    return action


@job
@related_action(action=related_pos_sale_order)
def action_confirm_pos_order(session, model_name, res_id):
    try:
        session.pool[model_name].action_button_confirm(
            session.cr, session.uid, [res_id], session.context)
        pos = session.pool[model_name].browse(session.cr, session.uid, res_id)
        return {'pos_id': pos.id}
    except Exception, e:
        raise RetryableJobError(e)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_job_id = fields.Many2one(
        'queue.job',
        string='POS Job',
        compute='_compute_pos_job_uuid',
    )
    pos_uuid = fields.Char(
        string='POS Job UUID',
        compute='_compute_pos_job_uuid',
    )

    @api.multi
    def _compute_pos_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_confirm_pos_order', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.pos_job_id = jobs and jobs[0] or False
            rec.pos_uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def action_button_confirm(self):
        if self._context.get('pos_async_process', False):
            self.ensure_one()
            if self._context.get('job_uuid', False):  # Called from @job
                return super(SaleOrder, self).action_button_confirm()
            if self.pos_job_id:
                message = _('Confirm POS Order')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Confirm POS Order' % self.name
            uuid = action_confirm_pos_order.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'confirm_pos_order')
        else:
            return super(SaleOrder, self).action_button_confirm()
