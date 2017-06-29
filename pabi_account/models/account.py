# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    line_item_summary = fields.Text(
        string='Items Summary',
        compute='_compute_line_item_summary',
        store=True,
        help="This field provide summary of items in move line with Qty."
    )

    @api.multi
    @api.depends('line_id.name')
    def _compute_line_item_summary(self):
        for rec in self:
            items = ['%s [%s]' % (x.name, x.quantity)
                     for x in rec.line_id
                     if (x.name != '/' and
                         x.account_id.user_type.report_type in ('income',
                                                                'expense'))]
            rec.line_item_summary = ", ".join(items)
