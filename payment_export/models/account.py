# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    lot_ids = fields.One2many(
        'cheque.lot',
        'journal_id',
        string='Cheque Lot',
        copy=False,
        help="Journal of type 'bank' can contain cheque lot",
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        compute='_compute_bank_id',
        readonly=True,
        help="Virtual bank accout. As 1 journal is for 1 bank",
    )
    export_config_ids = fields.One2many(
        'journal.export.config',
        string='Payment Export Pack'




        
    )

    @api.multi
    @api.depends()
    def _compute_bank_id(self):
        Bank = self.env['res.partner.bank']
        for journal in self:
            banks = Bank.search([('journal_id', '=', journal.id)])
            if banks and len(banks._ids) > 1:
                raise ValidationError(
                    _('Journal %s is used in more than '
                      'one bank account!') % (journal.name,))
            journal.bank_id = banks and banks[0] or False
