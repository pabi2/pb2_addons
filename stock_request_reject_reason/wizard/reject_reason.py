# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockRequestReject(models.TransientModel):

    _name = 'stock.request.reject'

    reject_reason_txt = fields.Char(
        string='Reason',
        readonly=False,
        size=500,
    )

    @api.one
    def confirm_reject(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        request_ids = self._context.get('active_ids')
        if request_ids is None:
            return act_close
        assert len(request_ids) == 1, "Only 1 stock request expected"
        request = self.env['stock.request'].browse(request_ids)
        request.reject_reason_txt = self.reject_reason_txt
        request.action_cancel()
        return act_close
