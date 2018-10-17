# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_sale_order(session, thejob):
    order_id = thejob.args[1]
    action = {
        'name': _("Sales Order"),
        'type': 'ir.actions.act_window',
        'res_model': "sale.order",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': order_id,
    }
    return action


@job
@related_action(action=related_sale_order)
def action_sale_create_invoice(session, model_name, res_id):
    try:
        session.pool[model_name].\
            action_invoice_create(session.cr, session.uid,
                                  [res_id], session.context)
        sale = session.pool[model_name].browse(session.cr, session.uid, res_id)
        invoice_ids = [x.id for x in sale.invoice_ids]
        return {'invoice_ids': invoice_ids}
    except Exception, e:
        raise FailedJobError(e)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    async_process = fields.Boolean(
        string='Create invoices in background?',
        default=True,
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
                ('action_sale_create_invoice', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.job_id = jobs and jobs[0] or False
            rec.uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def action_invoice_create(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(SaleOrder, self).action_invoice_create()
        # Enqueue
        if self.use_invoice_plan and self.async_process:
            if self.job_id:
                message = _('Creating Invoice(s)')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, _('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Creating Invoice(s)' % self.name
            uuid = action_sale_create_invoice.delay(
                session, self._name, self.id, description=description)
            job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_async_process.'
                                          'sale_invoice_plan')
        else:
            return super(SaleOrder, self).action_invoice_create()
