# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models
from .chartfield import ChartField


class AccountMoveLine(ChartField, models.Model):
    _inherit = 'account.move.line'
