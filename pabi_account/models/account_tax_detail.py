# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
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
    def _get_seq_search_domain(self, period):
        domain = super(AccountTaxDetail, self)._get_seq_search_domain(period)
        domain += [('taxbranch_id', '=', self.taxbranch_id.id)]
        return domain

    @api.model
    def _get_seq_name(self, period):
        name = 'TaxDetail-%s-%s' % (self.taxbranch_id.code, period.code)
        return name

    @api.model
    def _prepare_taxdetail_seq(self, period, sequence):
        vals = super(AccountTaxDetail, self)._prepare_taxdetail_seq(period,
                                                                    sequence)
        vals.update({'taxbranch_id': self.taxbranch_id.id})
        return vals


class AccountTaxDetailSequence(models.Model):
    _inherit = 'account.tax.detail.sequence'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
    )
