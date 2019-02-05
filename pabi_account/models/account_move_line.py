# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = 'sequence, date desc, id desc'

    sequence = fields.Integer('Sequence', default=0)
    date_reconciled = fields.Date(
        string='Full Reconciled Date',
        # related='reconcile_id.create_date',
        compute='_compute_date_reconciled',
        readonly=True,
        store=True,
        help="Dated when reconcile_id is set. "
        "Used in determine open items by date",
    )
    origin_ref = fields.Char(
        string='Origin Ref.',
        size=100,
        help="To be used during migration period to store origin number",
    )
    invoice_cancel = fields.Many2one(
        'account.invoice',
        compute='_compute_invoice_cancel',
        help="Functional field, use solely for _budget_eligible_move_lines",
    )

    @api.multi
    @api.depends('reconcile_id')
    def _compute_date_reconciled(self):
        # Find max date for each account.move.reconcile
        reconciles = self.mapped('reconcile_id')
        rec_dates = {}
        for reconcile in reconciles:
            dates = reconcile.line_id.mapped('date')
            rec_dates.update({reconcile.id: max(dates)})
        for rec in self:
            if rec.reconcile_id:
                rec.date_reconciled = rec_dates[rec.reconcile_id.id]

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
        narration_written = False
        for rec in self:
            # if rec.doctype in ('payment', 'receipt') and \
            #         not rec.move_id.narration:
            if rec.doctype in ('payment', 'receipt') and not narration_written:
                reconcile = rec.reconcile_id or rec.reconcile_partial_id
                move_lines = reconcile.line_id + reconcile.line_partial_ids
                inv_types = ('out_invoice', 'out_refund',
                             'out_invoice_debitnote',
                             'in_invoice_debitnote',
                             'in_invoice', 'in_refund')
                invoice_moves = move_lines.filtered(lambda l:
                                                    l.doctype in inv_types)
                if invoice_moves:
                    rec.move_id.narration = invoice_moves and \
                        invoice_moves[0].move_id.narration
                else:
                    bank_receipt = rec.bank_receipt_id
                    if bank_receipt:
                        bank_receipt.move_id.narration = rec.move_id.narration
                narration_written = True

    @api.multi
    def _budget_eligible_move_lines(self):
        """ More filtered to budget _budget_eligible_move_lines
        For move line created by cancelled invoice, do the filter also
        """
        move_lines = super(AccountMoveLine, self)._budget_eligible_move_lines()
        move_lines = move_lines.filtered(  # Too complicated to use SQL
            lambda l:
            not l.invoice_cancel or
            l.product_id.type == 'service' or
            l.product_id.valuation != 'real_time'
        )
        return move_lines

    @api.multi
    def _compute_invoice_cancel(self):
        for line in self:
            line.invoice_cancel = line.move_id.invoice_cancel_ids and \
                line.move_id.invoice_cancel_ids[0] or False
        return True
