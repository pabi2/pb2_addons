# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    longterm_invest_account_id = fields.Many2one(
        'account.account',
        string='Long Term Investment Account',
        domain=[('type', '=', 'other'),
                ('user_type.report_type', '=', 'asset')],
    )
