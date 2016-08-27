# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class AccountTaxDetail(models.Model):
    _inherit = 'account.tax.detail'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        index=True,
        compute='_compute_taxbranch_id',
        store=True,
    )
    _sql_constraints = [
        ('tax_sequence_uniq', 'unique(tax_sequence, period_id, taxbranch_id)',
         'Tax Detail Sequence has been used by other user, '
         'please validate document again'),
    ]

    @api.multi
    @api.depends('invoice_tax_id', 'voucher_tax_id')
    def _compute_taxbranch_id(self):
        for rec in self:
            if rec.invoice_tax_id:
                rec.taxbranch_id = rec.invoice_tax_id.invoice_id.taxbranch_id
            elif rec.voucher_tax_id:
                rec.taxbranch_id = rec.voucher_tax_id.invoice_id.taxbranch_id

    @api.model
    def _get_next_sequence(self, period_id):
        # Sequence run by Tax Branch
        if not self.taxbranch_id:
            raise ValidationError(_("Invoice has no NSTDA's Tax Branch!"))
        self._cr.execute("""
            select coalesce(max(tax_sequence), 0) + 1
            from account_tax_detail
            where period_id = %s
            and taxbranch_id = %s
        """, (period_id, self.taxbranch_id.id))
        return self._cr.fetchone()[0]
