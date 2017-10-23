# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _inherit = 'expense.create.supplier.invoice'

    pay_to = fields.Selection(
        selection_add=[('pettycash', 'Petty Cash')],
    )
