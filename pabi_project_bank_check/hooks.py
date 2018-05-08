# -*- coding: utf-8 -*-
from openerp import _
from openerp.exceptions import Warning as UserError


def pre_init_hook(cr):
    """ Check conclict module """
    conflict = 'account_voucher_no_auto_lines'
    cr.execute("""
        SELECT 1 FROM ir_module_module
        WHERE name = '%s' and state = 'installed'
    """ % conflict)
    if cr.fetchall():
        raise UserError(_('Module conflict: %s') % conflict)
