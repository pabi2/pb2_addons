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
class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    
    @api.multi
    def validate_picking(self):
        picking = self.env['stock.picking'].search([('origin','=',self.line_ids[0].move_line_id.move_id.document_id.source_document_id.name)])
        for pick in picking:
            pick.validate_picking()

    @api.multi
    def validate_picking_background(self):
        self.ensure_one()
        if self._context.get('job_uuid', False):  # Called from @job
            return self.validate_picking()
        session = ConnectorSession(self._cr, self._uid, self._context)
        description = 'POS Transfer Stock - %s' % (self.line_ids[0].move_line_id.move_id.document_id.source_document_id.name)
        uuid = action_done_async_process.delay(
            session, self._name, self.id, description=description)
        job = self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
    
    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            if voucher.line_ids and \
                voucher.line_ids[0].move_line_id and \
                voucher.line_ids[0].move_line_id.move_id.document and \
                'DV' in voucher.line_ids[0].move_line_id.move_id.document and \
                voucher.line_ids[0].move_line_id.move_id.document_id and \
                voucher.line_ids[0].move_line_id.move_id.document_id.source_document_id and \
                'POS' in voucher.line_ids[0].move_line_id.move_id.document_id.source_document_id.name:
                
                voucher.validate_picking_background()
        return result

