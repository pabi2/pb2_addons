# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART'),
         ('oversea', 'Oversea')
         ],
        string='Transfer Type',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="- DIRECT is transfer within same bank.\n"
        "- SMART is transfer is between different bank."
        "- Oversea won't be sent to Payment Export",
    )
    is_cheque_lot = fields.Boolean(
        string='Is Cheque Lot Available',
        compute='_compute_is_cheque_lot',
        help="True if the payment method also have cheque lot",
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot',
        string='Cheque Lot',
        domain="[('journal_id', '=', journal_id)]",
        ondelete="restrict",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supplier_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Supplier Bank Account',
        domain="[('partner_id', '=', partner_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supplier_bank_branch = fields.Char(
        string='Supplier Bank Branch',
        related='supplier_bank_id.bank_branch',
        readonly=True,
    )
    payment_export_id = fields.Many2one(
        'payment.export',
        string='Payment Export',
        readonly=True,
        ondelete='restrict',
    )

    @api.multi
    @api.depends('journal_id')
    def _compute_is_cheque_lot(self):
        for rec in self:
            Lot = self.env['cheque.lot']
            lots = Lot.search([('journal_id', '=', rec.journal_id.id)])
            rec.is_cheque_lot = lots and True or False

    @api.multi
    def onchange_partner_id(self, partner_id, journal_id, amount,
                            currency_id, ttype, date):
        res = super(AccountVoucher, self).\
            onchange_partner_id(partner_id, journal_id, amount,
                                currency_id, ttype, date)
        res = res or {'value': {}}
        res['value']['transfer_type'] = False
        return res

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        self.transfer_type = False

    @api.onchange('transfer_type')
    def _onchange_transfer_type(self):
        if self.transfer_type:
            default_bank = self.partner_id.bank_ids.filtered('default')
            self.supplier_bank_id = default_bank
        else:
            self.supplier_bank_id = False

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            Line = self.env['payment.export.line']
            lines = Line.search([('voucher_id', '=', voucher.id)])
            for line in lines:
                if line and line.export_id and line.export_id.state == 'done':
                    raise ValidationError(
                        _('This payment can not be unreconciled, '
                          'it was in already exported by %s')
                        % (line.export_id.name,))
        return super(AccountVoucher, self).cancel_voucher()

    @api.multi
    def onchange_journal(self, journal_id, line_ids, tax_id, partner_id,
                         date, amount, ttype, company_id):
        res = super(AccountVoucher, self).onchange_journal(
            journal_id, line_ids, tax_id, partner_id,
            date, amount, ttype, company_id)
        if not res:
            res = {'value': {}}
        res['value'].update({'cheque_lot_id': False})
        return res
