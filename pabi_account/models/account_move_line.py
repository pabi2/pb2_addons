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
                vals.pop('taxinvoice_taxbranch_id')
        return vals

    @api.multi
    def write(self, vals, check=True, update_check=True):
        res = super(AccountMoveLine, self).\
            write(vals, check=check, update_check=True)
        # For doctype PV/RC, get the narration of the counter invoice's move
        if vals.get('reconcile_id', False) or \
                vals.get('reconcile_partial_id', False):
            self._write_invoice_narration_to_payment()
        return res

    @api.multi
    def _write_invoice_narration_to_payment(self):
        for rec in self:
            if rec.doctype in ('payment', 'receipt') and not rec.narration:
                reconcile = rec.reconcile_id or rec.reconcile_partial_id
                move_lines = reconcile.line_id + reconcile.line_partial_ids
                inv_types = ('out_invoice', 'out_refund',
                             'out_invoice_debitnote',
                             'in_invoice_debitnote',
                             'in_invoice', 'in_refund')
                invoice_moves = move_lines.filtered(lambda l:
                                                    l.doctype in inv_types)
                rec.narration = invoice_moves and \
                    invoice_moves[0].move_id.narration
