# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrderForceDone(models.TransientModel):

    _inherit = 'purchase.order.force.done'

    force_done_file = fields.Binary(
        string="Attach File",
        required=True,
    )

    @api.one
    def confirm_force_done(self):
        Order = self.env['purchase.order']
        Attachment = self.env['ir.attachment']
        file = self.force_done_file
        active_id = self._context['active_ids'][0]
        order_name = Order.browse(active_id).name
        Attachment.create({
            'name': order_name+"_force_done_reason",
            'datas': file,
            'datas_fname': order_name+"_force_done_reason.pdf",
            'res_model': 'purchase.order',
            'res_id': active_id,
            'type': 'binary'
        })
        return super(PurchaseOrderForceDone, self).confirm_force_done()
