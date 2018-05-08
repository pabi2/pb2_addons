# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    lot_ids = fields.One2many(
        'cheque.lot',
        'journal_id',
        string='Cheque Lot',
        copy=False,
        help="Journal of type 'bank' can contain cheque lot",
    )
    export_config_ids = fields.One2many(
        'journal.export.config',
        'journal_id',
        string='Payment Export Pack',
    )


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
        required=False,
        ondelete='set null',
    )
    _sql_constraints = [
        ('export_config_uniq', 'unique(journal_id, transfer_type, config_id)',
         'Duplicated config for the same transfer type not allowed!')]
