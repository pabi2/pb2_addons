# -*- coding: utf-8 -*-
import ast

from openerp import models, api, _
from openerp.exceptions import RedirectWarning, Warning as UserError
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
def action_invoice_create_enqueue(session, model_name, res_id):
    try:
        session.pool[model_name].\
            action_invoice_create(session.cr, session.uid,
                                  [res_id], session.context)
    except Exception, e:
        raise FailedJobError(e)
    purchase = session.pool[model_name].browse(session.cr, session.uid, res_id)
    invoice_ids = [x.id for x in purchase.invoice_ids]
    return {'invoice_ids': invoice_ids}


class PurchaseOrder(PabiAsync, models.Model):
    _inherit = 'purchase.order'

    @api.one
    def action_invoice_create(self):
        if self._context.get('job_uuid', False):  # Called from job queue
            return super(PurchaseOrder, self).action_invoice_create()
        # Enqueue
        if self._context.get('async_process', False):
            func = 'action_invoice_create_enqueue'
            self._check_queue(func, doc_name=self.name)
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = '%s - Create Supplier Invoice(s)' % self.name
            action_invoice_create_enqueue.delay(session, self._name, self.id,
                                                description=description)
            self._cr.commit()
            self._check_queue(func, doc_name=self.name)
        else:
            return super(PurchaseOrder, self).action_invoice_create()
