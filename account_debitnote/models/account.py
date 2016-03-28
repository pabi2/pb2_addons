# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(
        [('sale', 'Sale'),
         ('sale_refund', 'Sale Refund'),
         ('sale_debitnote', 'Sale Debit Note'),
         ('purchase', 'Purchase'),
         ('purchase_refund', 'Purchase Refund'),
         ('purchase_debitnote', 'Purchase Debit Note'),
         ('cash', 'Cash'),
         ('bank', 'Bank and Checks'),
         ('general', 'General'),
         ('situation', 'Opening/Closing Situation')],
        help="""Select 'Sale' for customer invoices journals.
            Select 'Purchase' for supplier invoices journals.
            Select 'Cash' or 'Bank' for journals that are used
            in customer or supplier payments.
            Select 'General' for miscellaneous operations journals.
            Select 'Opening/Closing Situation' for entries generated
            for new fiscal years.""")
