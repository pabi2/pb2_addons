# -*- coding: utf-8 -*-
from openerp import models
from .chartfield import \
    ChartField


class AccountInvoiceLine(ChartField, models.Model):
    _inherit = 'account.invoice.line'
