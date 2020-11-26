# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


# สร้าง FIELD
class PrintInternalChargeJournalEntriesWizard(models.TransientModel):
    _name = 'print.internal.charge.journal.entries.wizard'


    @api.multi
    def action_print_internal_charge_journal_entries(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        report_name = 'internal_charge_journal_entries'
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
