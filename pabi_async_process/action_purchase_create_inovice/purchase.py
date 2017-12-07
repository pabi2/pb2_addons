# -*- coding: utf-8 -*-
from openerp import models, api, _
from ..models.common import PabiAsync

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_purchase_order(session, thejob):
    order_id = thejob.args[1]
    action = {
        'name': _("Purchase Order"),
        'type': 'ir.actions.act_window',
        'res_model': "purchase.order",
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': order_id,
    }
    return action


@job
@related_action(action=related_purchase_order)
def action_purchase_create_invoice(session, model_name, res_id):
    try:
        session.pool[model_name].\
            action_invoice_create(session.cr, session.uid,
                                  [res_id], session.context)
        purchase = session.pool[model_name].browse(session.cr,
                                                   session.uid, res_id)
        invoice_ids = [x.id for x in purchase.invoice_ids]
        return {'invoice_ids': invoice_ids}
    except Exception, e:
        raise FailedJobError(e)


class PurchaseOrder(PabiAsync, models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_invoice_create(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return super(PurchaseOrder, self).action_invoice_create()
        # Enqueue
        if self._context.get('async_process', False):
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Create Supplier Invoice(s)' % self.name
            uuid = action_purchase_create_invoice.delay(
                session, self._name, self.id, description=description)
            # Checking for running task, use the same signature as delay()
            task_name = "%s('%s', %s)" % \
                ('action_purchase_create_invoice', self._name, self.id)
            self._check_queue(task_name, desc=self.name,
                              type='always', uuid=uuid)
        else:
            return super(PurchaseOrder, self).action_invoice_create()
