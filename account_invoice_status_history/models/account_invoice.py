# -*- coding: utf-8 -*-
from openerp import models
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class AccountInvoice(LogCommon, models.Model):
    _inherit = 'account.invoice'
