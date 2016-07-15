# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError


class InvoiceVoucherTaxDetail(object):

    @api.multi
    def _check_tax_detail_info(self):
        for doc in self:
            if doc.type not in ('in_refund', 'in_invoice', 'payment'):
                continue
            for tax in doc.tax_line:
                if tax.tax_code_type != 'normal':
                    continue
                for detail in tax.detail_ids:
                    if (not detail.partner_id or
                            not detail.invoice_number or
                            not detail.invoice_date):
                        raise UserError(
                            _('Some data in Tax Detail is not filled!'))
        return True

    @api.model
    def _get_valid_date_range(self, months):
        Period = self.env['account.period']
        period = Period.find(fields.Date.context_today(self))[:1]
        date_stop = datetime.strptime(period.date_stop, '%Y-%m-%d').date()
        date_start = datetime.strptime(period.date_start, '%Y-%m-%d').date()
        date_start = date_start + relativedelta.relativedelta(months=-months+1)
        return date_start, date_stop

    @api.model
    def _get_date_document(self, doc):
        # Get document date, either invoice or voucher
        if doc.type in ('in_refund', 'in_invoice'):
            return doc.date_invoice
        elif doc.type in ('payment'):
            return doc.date
        else:
            raise ValidationError(_('Invalid Document Type!'))

    @api.multi
    def _assign_detail_tax_sequence(self):
        Period = self.env['account.period']
        TaxDetail = self.env['account.tax.detail']
        ConfParam = self.env['ir.config_parameter']
        months = ConfParam.get_param('number_month_tax_addition')
        tax_months = months and int(months) or 6
        date_start, date_stop = self._get_valid_date_range(tax_months)

        for doc in self:
            # Skip if not Purchase side
            if doc.type not in ('in_refund', 'in_invoice', 'payment'):
                continue
            date_doc = self._get_date_document(doc)
            period_id = Period.find(date_doc)[:1].id
            for tax in doc.tax_line:
                # Skip if Undue Tax
                if tax.tax_code_type != 'normal':
                    continue
                for detail in tax.detail_ids:
                    invoice_date = datetime.strptime(detail.invoice_date,
                                                     '%Y-%m-%d').date()
                    if date_start <= invoice_date <= date_stop:
                        next_seq = TaxDetail._get_next_sequence(period_id)
                        detail.write({'tax_sequence': next_seq,
                                      'period_id': period_id,
                                      })
                    else:
                        add_period_id = Period.find(detail.invoice_date)[:1].id
                        next_seq = TaxDetail._get_next_sequence(add_period_id)
                        detail.write({'tax_sequence': next_seq,
                                      'period_id': add_period_id,
                                      'addition': True,
                                      })


class AccountTaxDetail(models.Model):
    _name = 'account.tax.detail'

    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
        ondelete='cascade',
        index=True,
    )
    voucher_tax_id = fields.Many2one(
        'account.voucher.tax',
        ondelete='cascade',
        index=True,
    )
    tax_sequence = fields.Integer(
        string='Sequence',
        readonly=True,
        help="Running sequence for the same period. Reset every period",
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    addition = fields.Boolean(
        strin='Past Period Tax',
        default=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    invoice_number = fields.Char(
        string='Tax Invoice Number',
    )
    invoice_date = fields.Date(
        string='Invoice Date',
    )
    base = fields.Float(
        string='Base',
    )
    amount = fields.Float(
        string='Tax',
    )

    _sql_constraints = [
        ('tax_sequence_uniq', 'unique(tax_sequence, period_id)',
            'Tax Detail Sequence has been used by other user, '
            'please validate document again'),
    ]

    @api.model
    def _get_next_sequence(self, period_id):
        self._cr.execute("""
            select coalesce(max(tax_sequence), 0) + 1
            from account_tax_detail
            where period_id = %s
        """, (period_id,))
        return self._cr.fetchone()[0]
