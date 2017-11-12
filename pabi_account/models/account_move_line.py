# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = 'sequence, date desc, id desc'

    sequence = fields.Integer('Sequence', default=0)

    @api.model
    def _update_analytic_dimension(self, vals):
        vals = super(AccountMoveLine, self)._update_analytic_dimension(vals)
        # Remove taxbranch_id, it shouldn't be for move line
        if 'taxbranch_id' in vals:
            # tax_taxbranch_id is prepared form the calling document
            # it use invoice's taxbranch
            if vals.get('taxinvoice_taxbranch_id', False):
                vals['taxbranch_id'] = vals.get('taxinvoice_taxbranch_id')
        return vals
