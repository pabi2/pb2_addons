# -*- coding: utf-8 -*-

from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    bill_uid = fields.Many2one(
        'res.users',
        string='Received by',
        states={'draft': [('readonly', False)]},
    )
    date_bill = fields.Date(
        string='Billing Date',
        states={'draft': [('readonly', False)]},
    )
    bill_note = fields.Text(
        string='Additional Info',
        states={'draft': [('readonly', False)]},
    )
    bill_number = fields.Char(
        string='Billing No.',
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def create_bill_no(self):
        bill_no = self.env['ir.sequence'].get('bill.number'),
        self.bill_number = bill_no[0]
