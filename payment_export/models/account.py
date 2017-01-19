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
        'journal_id',
        string='Payment Export Pack',
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


class JournalExportConfig(models.Model):
    _name = 'journal.export.config'
    _description = 'Document Export Config criteria for this journal'

    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        index=True,
        readonly=True,
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART')
         ],
        string='Transfer Type',
        required=True,
        help="- DIRECT is transfer within same bank.\n"
        "- SMART is transfer is between different bank."
    )
    config_id = fields.Many2one(
        'document.export.config',
        string='Export Pack',
        required=True,
    )
    _sql_constraints = [
        ('export_config_uniq', 'unique(journal_id, transfer_type, config_id)',
         'Duplicated config for the same transfer type not allowed!')]
