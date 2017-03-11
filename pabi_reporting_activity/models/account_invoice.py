# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    rpt_activity_id = fields.Many2one(
        'account.activity',
        string='Rpt Activity',
        required=True,
    )

    @api.multi
    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        for rec in self:
            # If activity_id is selected, rpt_activity_id always follows
            if rec.activity_id:
                rec.rpt_activity_id = rec.activity_id
