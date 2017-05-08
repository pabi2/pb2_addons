# -*- coding: utf-8 -*-
from openerp import models, fields
from .chartfield import MergedChartField


class AccountInvoiceLine(MergedChartField, models.Model):
    _inherit = 'account.invoice.line'

    chartfield_id = fields.Many2one(
        domain=False,
        help="For invoice, display all dimensions",
    )
