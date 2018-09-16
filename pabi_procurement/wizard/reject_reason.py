# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseRequisitionReject(models.TransientModel):

    _name = 'purchase.requisition.reject'

    reject_reason_txt = fields.Char(
        string="Rejected Reason",
        readonly=False,
        size=500,
    )

    @api.one
    def confirm_reject(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        requisition_ids = self._context.get('active_ids')
        if requisition_ids is None:
            return act_close
        assert len(requisition_ids) == 1, "Only 1 Call for Bids expected"
        requisition = self.env['purchase.requisition'].browse(requisition_ids)
        requisition.reject_reason_txt = self.reject_reason_txt
        requisition.signal_workflow('rejected')
        return act_close
