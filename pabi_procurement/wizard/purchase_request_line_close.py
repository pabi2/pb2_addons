# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class PurchaseRequestLineClose(models.TransientModel):
    _name = "purchase.request.line.close"
    _description = "Close Purchase Request Line"

    confirm_close = fields.Boolean(
        string='Confirm Closing Purchase Request Line'
    )

    @api.one
    def close_line(self):
        if not self.confirm_close:
            raise ValidationError(
                _("Can't close purchase request lines."
                  " Please check the confirm box.")
            )
        ReqLine = self.env['purchase.request.line']
        active_ids = self._context['active_ids']
        lines = ReqLine.search([('id', 'in', active_ids)])
        for line in lines:
            if line.state == 'close':
                raise ValidationError(
                    _("Can't close purchase request lines."
                      " Some lines are already closed.")
                )
            elif line.requisition_state != 'none':
                raise ValidationError(
                    _("Each Request bid status should be 'No Bid' : %s"
                      % (line.request_id.name,))
                )
            else:
                line.state = 'close'
