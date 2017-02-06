# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    # Change order debit first then credit. Can't do much as it affect perf
    _order = 'move_id, debit desc, credit desc , account_id'

    @api.model
    def _update_analytic_dimension(self, vals):
        vals = super(AccountMoveLine, self)._update_analytic_dimension(vals)
        # Remove taxbranch_id, it shouldn't be for move line
        if 'taxbranch_id' in vals:
            # tax_taxbranch_id is prepared form the calling document
            # it use invoice's taxbranch
            vals['taxbranch_id'] = vals.get('taxinvoice_taxbranch_id', False)
        return vals
