# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.api import Environment
from openerp import SUPERUSER_ID


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    control_ext_charge_only = fields.Boolean(
        string='Control External Charge Only',
        default=False,
        help="Budget check only External Charge, bypass Internal Charge",
    )
