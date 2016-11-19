# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountPeriod(models.Model):
    _inherit = 'account.period'

    taxdetail_sequence_ids = fields.One2many(
        'account.tax.detail.sequence',
        'period_id',
        string='Tax Detail Sequence',
    )
