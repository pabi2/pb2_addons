# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AccountAccount(orm.Model):
    _inherit = 'account.account'

    _columns = {
        'centralized': fields.boolean(
            'Centralized',
            help="If flagged, no details will be displayed in "
                 "the General Ledger report (the webkit one only), "
                 "only centralized amounts per period."),
    }
    _defaults = {
        'centralized': False,
    }
