# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def check_missing_tax(self):
        res = False  # Force not check missing tax
        return res

    @api.multi
    def _check_tax_detail_info(self):
        for invoice in self:
            if invoice.type not in ('in_refund', 'in_invoice'):
                continue
            for tax in invoice.tax_line:
                for detail in tax.detail_ids:
                    if (not detail.partner_id or
                            not detail.invoice_number or
                            not detail.invoice_date):
                        raise UserError(
                            _('Some data in Tax Detail is not filled!'))

    @api.multi
    def _assign_detail_tax_sequence(self):
        Period = self.env['account.period']
        TaxDetail = self.env['account.invoice.tax.detail']
        ConfParam = self.env['ir.config_parameter']
        months = ConfParam.get_param('number_month_tax_addition')
        tax_months = months and int(months) or 6
        for invoice in self:
            if invoice.type not in ('in_refund', 'in_invoice'):
                continue
            period_id = Period.find(invoice.date_invoice)[:1].id
            for tax in invoice.tax_line:
                for detail in tax.detail_ids:
                    invoice_date = datetime.strptime(detail.invoice_date,
                                                     '%Y-%m-%d')
                    today = datetime.strptime(fields.Date.context_today(self),
                                              '%Y-%m-%d')
                    r = relativedelta.relativedelta(today, invoice_date)
                    # > 6 months, use its own period
                    if r.months > tax_months or \
                            (r.months == tax_months and r.days > 0):
                        add_period_id = Period.find(detail.invoice_date)[:1].id
                        next_seq = TaxDetail._get_next_sequence(add_period_id)
                        detail.write({'tax_sequence': next_seq,
                                      'period_id': add_period_id,
                                      'addition': True,
                                      })
                    else:
                        next_seq = TaxDetail._get_next_sequence(period_id)
                        detail.write({'tax_sequence': next_seq,
                                      'period_id': period_id,
                                      })

    @api.multi
    def action_move_create(self):
        self._check_tax_detail_info()
        result = super(AccountInvoice, self).action_move_create()
        self._assign_detail_tax_sequence()
        return result


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    detail_ids = fields.One2many(
        'account.invoice.tax.detail',
        'invoice_tax_id',
        string='Tax Detail',
    )

    @api.model
    def create(self, vals):
        invoice_tax = super(AccountInvoiceTax, self).create(vals)
        detail = {'invoice_tax_id': invoice_tax.id}
        self.env['account.invoice.tax.detail'].create(detail)
        return invoice_tax


class AccountInvoiceTaxDetail(models.Model):
    _name = 'account.invoice.tax.detail'

    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
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
            from account_invoice_tax_detail
            where period_id = %s
        """, (period_id,))
        return self._cr.fetchone()[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
