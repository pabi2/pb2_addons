# -*- coding: utf-8 -*-

from openerp import models, fields, api
import time


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # Customer Payment
    date_cheque = fields.Date(
        string='Cheque Date',
        default=lambda *a: time.strftime('%Y-%m-%d'),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    number_cheque = fields.Char(
        string='Cheque No.',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    bank_cheque = fields.Char(
        string='Bank',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    branch_cheque = fields.Char(
        string='Bank Branch',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # Supplier Payment
    date_value = fields.Date(
        string='Value Date',  # bank transfer date
        readonly=True,
        states={'draft': [('readonly', False)]},
    )


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
        compute='_move_line_get_invoice_id',
        store=True,
    )

    @api.multi
    @api.depends('move_line_id')
    def _move_line_get_invoice_id(self):
        for rec in self:
            if not rec.id:
                return []
            query = """ SELECT i.id
                FROM account_voucher_line vl,
                account_move_line ml, account_invoice i
                WHERE vl.move_line_id = ml.id and ml.move_id = i.move_id
                AND vl.id = %s """
            self._cr.execute(query, (rec.id,))
            row = self._cr.fetchone() or False
            rec.invoice_id = row and row[0] or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
