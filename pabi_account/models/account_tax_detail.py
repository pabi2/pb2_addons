# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountTaxDetail(models.Model):
    _inherit = 'account.tax.detail'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        index=True,
    )
    _sql_constraints = [
        ('tax_sequence_uniq',
         'unique(doc_type,tax_sequence,period_id,taxbranch_id,cancel_entry)',
         'Tax Detail Sequence has been used by other user, '
         'please validate document again'),
    ]

    @api.model
    def create(self, vals):
        rec = super(AccountTaxDetail, self).create(vals)
        if rec.invoice_tax_id:
            rec.taxbranch_id = rec.invoice_tax_id.invoice_id.taxbranch_id
        elif rec.voucher_tax_id:
            rec.taxbranch_id = rec.voucher_tax_id.invoice_id.taxbranch_id
        # if not rec.taxbranch_id:
        #   raise ValidationError(_('No taxbranch_id when create tax detail'))
        return rec

    @api.multi
    @api.depends('invoice_tax_id', 'voucher_tax_id')
    def _compute_taxbranch_id(self):
        for rec in self:
            if rec.invoice_tax_id:
                rec.taxbranch_id = rec.invoice_tax_id.invoice_id.taxbranch_id
            elif rec.voucher_tax_id:
                rec.taxbranch_id = rec.voucher_tax_id.invoice_id.taxbranch_id

    @api.model
    def _get_seq_search_domain(self, doc_type, period):
        domain = super(AccountTaxDetail, self).\
            _get_seq_search_domain(doc_type, period)
        domain += [('taxbranch_id', '=', self.taxbranch_id.id)]
        return domain

    @api.model
    def _get_seq_name(self, doc_type, period):
        name = 'TaxDetail-%s-%s-%s' % (doc_type, self.taxbranch_id.code,
                                       period.code)
        return name

    @api.model
    def _prepare_taxdetail_seq(self, doc_type, period, sequence):
        vals = super(AccountTaxDetail, self).\
            _prepare_taxdetail_seq(doc_type, period, sequence)
        vals.update({'taxbranch_id': self.taxbranch_id.id})
        return vals


class AccountTaxDetailSequence(models.Model):
    _inherit = 'account.tax.detail.sequence'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
    )
