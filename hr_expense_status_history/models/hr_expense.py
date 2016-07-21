# -*- coding: utf-8 -*-
from openerp import models
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class HRExpenseExpense(LogCommon, models.Model):
    _inherit = 'hr.expense.expense'
