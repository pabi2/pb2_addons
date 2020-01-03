# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError

@job
def action_done_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].validate_picking_background(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def validate_picking(self):
        picking = self.env['stock.picking'].search([('origin','=',self.source_document)])
        for pick in picking:
            pick.validate_picking()

    @api.multi
    def validate_picking_background(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return self.validate_picking()
        session = ConnectorSession(self._cr, self._uid, self._context)
        description = 'POS Transfer Stock - %s' % (self.source_document)
        uuid = action_done_async_process.delay(
            session, self._name, self.id, description=description)
        job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
    
    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if 'POS' in invoice.source_document:
                invoice.validate_picking_background()
        return result
