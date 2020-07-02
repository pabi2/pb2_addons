# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp import SUPERUSER_ID


class InvoiceVoucherTaxDetail(object):

    @api.multi
    def _compute_sales_tax_detail(self):
        TaxDetail = self.env['account.tax.detail']
        for doc in self:
            if doc.type in ('in_refund', 'in_invoice', 'payment'):
                continue
            # Auto create tax detail for Sales Cycle only
            for tax in doc.tax_line:
                if tax.tax_code_type != 'normal':
                    continue
                invoice_tax_id = False
                voucher_tax_id = False
                doc_date = False
                domain = []
                if doc._name == 'account.invoice':
                    invoice_tax_id = tax.id
                    doc_date = doc.date_invoice
                    domain = [('invoice_tax_id', '=', tax.id)]
                if doc._name == 'account.voucher':
                    voucher_tax_id = tax.id
                    doc_date = doc.date
                    domain = [('voucher_tax_id', '=', tax.id)]
                sign = doc.type in ('out_refund') and -1 or 1
                vals = TaxDetail.\
                    _prepare_tax_detail(invoice_tax_id,
                                        voucher_tax_id,
                                        'sale',
                                        doc.partner_id.id,
                                        doc.number_preprint or doc.number,
                                        doc_date,
                                        sign * tax.base,
                                        sign * tax.amount)
                # For update sequence preprint
                vals = TaxDetail._create_sequence_preprint(
                    invoice_tax_id, voucher_tax_id, doc, vals, doc_date)
                detail = TaxDetail.search(domain)
                if detail:
                    detail.write(vals)
                else:
                    TaxDetail.create(vals)

    @api.multi
    def _check_tax_detail_info(self):
        for doc in self:
            taxes = doc.tax_line.filtered(lambda l:
                                          l.tax_code_type == 'normal')
            for tax in taxes:
                if tax.detail_ids.filtered(lambda l: not (l.partner_id and
                                                          l.invoice_number and
                                                          l.invoice_date)):
                    raise ValidationError(
                        _('Some data in Tax Detail is not filled!'))
        return True

    @api.model
    def _get_date_document(self, doc):
        # Get document date, either invoice or voucher
        if doc.type in ('in_refund', 'in_invoice',
                        'out_refund', 'out_invoice'):
            return doc.date_invoice
        elif doc.type in ('payment', 'receipt'):
            return doc.date
        else:
            raise ValidationError(_('Invalid Document Type!'))

    @api.multi
    def _assign_detail_tax_sequence(self):
        for doc in self:
            date_doc = self._get_date_document(doc)
            for tax in doc.tax_line:
                # Skip if Undue Tax
                if tax.tax_code_type != 'normal':
                    continue
                for detail in tax.detail_ids:
                    detail._set_next_sequence(date_doc)

    @api.multi
    def _check_income_tax_from(self):
        for linetax in self.invoice_line:
            for taxid in linetax.invoice_line_tax_id._ids:
                taxlineid = self.env['account.tax'].search([('id','=',taxid)]).description
                if taxlineid == 'WHTP1':
                    if self.income_tax_form == 'pnd3' and taxlineid == 'WHTP1' :
                        continue
                    else:
                        raise ValidationError(
                                _('- WHTP1 must be related with PND3 only.'))
                elif taxlineid == 'WHTC1':
                    if self.income_tax_form == 'pnd53' and taxlineid == 'WHTC1':
                        continue
                    elif self.income_tax_form == 'pnd54' and taxlineid == 'WHTC1':
                        continue
                    else:
                         raise ValidationError(
                                _('- WHTC1 must be related with PND53 or PND54 only.'))
        return True
#////////////////////////////////////////////////////////////////////////////////////////////////

class AccountTaxDetail(models.Model):
    _name = 'account.tax.detail'

    doc_type = fields.Selection(
        [('sale', 'Sales'),
         ('purchase', 'Purchase')],
        string='Document Type',
        readonly=False,
        required=True,
    )
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
    move_line_id = fields.Many2one(
        'account.move.line',
        ondelete='cascade',
        index=True,
    )
    tax_id = fields.Many2one(
        'account.tax',
        ondelete='cascade',
        readonly=False,
    )
    tax_sequence = fields.Integer(
        string='Sequence',
        readonly=True,
        help="Running sequence for the same period. Reset every period",
    )
    tax_sequence_display = fields.Char(
        string='Sequence',
        compute='_compute_tax_report',
        store=True,
    )
    report_period_id = fields.Many2one(
        'account.period',
        string='Document Period',
        compute='_compute_tax_report',
        store=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    addition = fields.Boolean(
        string='Past Period Tax',
        default=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    invoice_number = fields.Char(
        string='Tax Invoice Number',
        size=500,
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
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        help="Foreign currency",
    )
    base_company = fields.Float(
        string='Base',
        compute='_compute_tax_report',
        store=True,
        help="Base in company currency",
    )
    amount_company = fields.Float(
        string='Tax',
        compute='_compute_tax_report',
        store=True,
        help="Tax in company currency",
    )
    date_doc = fields.Date(
        string='Document Date',
        help="Invoice or payment posting date",
    )
    cancel = fields.Boolean(
        string='Cancelled',
        default=False,
        help="If the Invoice/Voucher is set to cancelled, tax will show 0.0",
    )
    ref_move_id = fields.Many2one(
        'account.move',
        string='Ref Journal Entry',
        ondelete='restrict',
        help="Referene to move_id of either Invoice / Payment / Account Move",
    )
    _sql_constraints = [
        ('tax_sequence_uniq', 'unique(doc_type, tax_sequence, period_id)',
            'Tax Detail Sequence has been used by other user, '
            'please validate document again'),
    ]

    def init(self, cr):
        # This is a helper to guess "old" tax_id from tax_code
        TaxDetail = self.pool['account.tax.detail']
        tax_detail_ids = TaxDetail.search(cr, SUPERUSER_ID,
                                          [('tax_id', '=', False)])
        if tax_detail_ids:
            tax_details = TaxDetail.browse(cr, SUPERUSER_ID, tax_detail_ids)
            for tax_detail in tax_details:
                tax_code = ((tax_detail.invoice_tax_id and
                             tax_detail.invoice_tax_id.tax_code_id) or
                            (tax_detail.voucher_tax_id and
                             tax_detail.voucher_tax_id.tax_code_id) or
                            False)
                if not tax_code:
                    continue
                tax_id = self._get_tax_id(cr, SUPERUSER_ID, tax_code, False)
                TaxDetail.write(cr, SUPERUSER_ID, [tax_detail.id],
                                {'tax_id': tax_id})

    @api.model
    def _get_valid_date_range(self, months):
        Period = self.env['account.period']
        period = Period.find(fields.Date.context_today(self))[:1]
        date_stop = datetime.strptime(period.date_stop, '%Y-%m-%d').date()
        date_start = datetime.strptime(period.date_start, '%Y-%m-%d').date()
        date_start = date_start + \
            relativedelta.relativedelta(months=-months + 1)
        return date_start, date_stop

    @api.multi
    def _set_next_sequence(self, date_doc=None):
        for rec in self:
            if rec.tax_sequence:
                continue
            months = rec.env.user.company_id.number_month_tax_addition
            tax_months = months and int(months) or 6
            date_start, date_stop = rec._get_valid_date_range(tax_months)
            invoice_date = datetime.strptime(rec.invoice_date,
                                             '%Y-%m-%d').date()
            sequence_date = False
            # If this is clear undue VAT case
            if self._context.get('recognize_vat', False):
                sequence_date = self._context.get('date_clear_undue')
            elif date_doc:  # Date from document, take priority
                sequence_date = date_doc
            elif rec.ref_move_id.date:  # For JV/JN, use move date
                sequence_date = rec.ref_move_id.date
            elif rec.invoice_date:  # Else use tax detail's invoice date
                sequence_date = rec.invoice_date
            if not sequence_date:
                raise ValidationError(_('Date not found for tax detail seq'))
            period = self.env['account.period'].find(sequence_date)[:1]
            ref_move_id = rec.ref_move_id.id or \
                rec.invoice_tax_id.invoice_id.move_id.id or \
                rec.voucher_tax_id.voucher_id.move_id.id or \
                rec.move_line_id.move_id.id or False
            if date_start <= invoice_date <= date_stop:
                next_seq = rec._get_next_sequence(period)
                rec.write({'tax_sequence': next_seq,
                           'period_id': period.id,
                           'date_doc': date_doc,
                           'ref_move_id': ref_move_id,
                           })
            else:
                Period = self.env['account.period']
                add_period = Period.find(rec.invoice_date)[:1]
                next_seq = rec._get_next_sequence(add_period)
                rec.write({'tax_sequence': next_seq,
                           'period_id': add_period.id,
                           'date_doc': date_doc,
                           'ref_move_id': ref_move_id,
                           'addition': True,
                           })

    @api.model
    def _get_tax_id(self, tax_code, validate=True):
        if not tax_code:
            raise ValidationError(_('No tax code found!'))
        tax = self.env['account.tax'].search([('tax_code_id', '=',
                                               tax_code.id)])
        if validate:
            if len(tax) != 1:
                raise ValidationError(
                    _("Invalid tax setup for '%s'\n"
                      "(1 tax != 1 tax code)") % (tax_code.name,))
        return tax[0].id

    @api.model
    def _prepare_tax_detail_dict(self, invoice_tax_id, voucher_tax_id,
                                 doc_type, partner_id, invoice_number,
                                 invoice_date, base, amount,
                                 move_line_id=False):
        vals = {
            'invoice_tax_id': invoice_tax_id,
            'voucher_tax_id': voucher_tax_id,
            'doc_type': doc_type,
            'partner_id': partner_id,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'base': base,
            'amount': amount,
            'move_line_id': move_line_id,
        }
        return vals

    @api.model
    def _prepare_tax_detail(
            self, invoice_tax_id, voucher_tax_id, doc_type,
            partner_id, invoice_number, invoice_date, base, amount):
        vals = self._prepare_tax_detail_dict(
            invoice_tax_id, voucher_tax_id, doc_type,
            partner_id, invoice_number, invoice_date, base, amount)
        model = invoice_tax_id and \
            'account.invoice.tax' or 'account.voucher.tax'
        doc_tax_id = invoice_tax_id or voucher_tax_id
        tax_code = self.env[model].browse(doc_tax_id).tax_code_id
        vals.update({'tax_id': self._get_tax_id(tax_code)})
        return vals

    @api.model
    def _create_sequence_preprint(self, invoice_tax_id, voucher_tax_id, doc,
                                  vals, invoice_date):
        # Generate sequence preprint
        seq_name = invoice_tax_id and 'invoice.tax.preprint'\
            or 'receipt.tax.preprint'
        preprint_number = self.env['ir.sequence.preprint'].next_by_code(
            seq_name, sequence_date=invoice_date)
        vals['invoice_number'] = preprint_number
        doc.update({'number_preprint': preprint_number})
        return vals

    @api.multi
    @api.depends('tax_sequence')
    def _compute_tax_report(self):
        for rec in self:
            if rec.period_id and rec.tax_sequence:
                date_start = rec.period_id.date_start
                # Sequence Display
                mo = datetime.strptime(date_start, '%Y-%m-%d').date().month
                month = '{:02d}'.format(mo)
                sequence = '{:04d}'.format(rec.tax_sequence)
                rec.tax_sequence_display = '%s/%s' % (month, sequence)
                # Reporting Period
                company = False
                if rec.invoice_tax_id:
                    invoice = rec.invoice_tax_id.invoice_id
                    rec.report_period_id = invoice.period_id
                    company = invoice.company_id
                elif rec.voucher_tax_id:
                    voucher = rec.voucher_tax_id.voucher_id
                    if voucher.recognize_vat_move_id:
                        rec.report_period_id = \
                            voucher.recognize_vat_move_id.period_id
                    else:
                        rec.report_period_id = voucher.period_id
                    company = voucher.company_id
                else:
                    rec.report_period_id = rec.period_id
                # Make sure report_period is not before tax period
                if rec.report_period_id.date_start < rec.period_id.date_start:
                    rec.report_period_id = rec.period_id
                # Compute by currency
                if rec.currency_id:  # to company currency
                    company_currency = company.currency_id
                    from_currency = \
                        rec.currency_id.with_context(date=rec.date_doc)
                    rec.base_company = \
                        from_currency.compute(rec.base, company_currency)
                    rec.amount_company = \
                        from_currency.compute(rec.amount, company_currency)
                else:
                    rec.base_company = rec.base
                    rec.amount_company = rec.amount

    @api.model
    def _get_seq_search_domain(self, doc_type, period):
        domain = [('doc_type', '=', doc_type), ('period_id', '=', period.id)]
        return domain

    @api.model
    def _get_next_sequence(self, period):
        TaxDetailSequence = self.env['account.tax.detail.sequence']
        domain = self._get_seq_search_domain(self.doc_type, period)
        seq = TaxDetailSequence.search(domain, limit=1)
        if not seq:
            seq = self._create_sequence(self.doc_type, period)
        self = self.with_context({'fiscalyear_id': period.fiscalyear_id.id})
        Sequence = self.env['ir.sequence']
        return int(Sequence.next_by_id(seq.sequence_id.id))

    @api.model
    def _get_seq_name(self, doc_type, period):
        name = 'TaxDetail-%s-%s' % (doc_type, period.code,)
        return name

    @api.model
    def _prepare_taxdetail_seq(self, doc_type, period, new_sequence):
        vals = {
            'doc_type': doc_type,
            'period_id': period.id,
            'sequence_id': new_sequence.id,
        }
        return vals

    @api.model
    def _create_sequence(self, doc_type, period):
        seq_vals = {'name': self._get_seq_name(doc_type, period),
                    'implementation': 'no_gap'}
        new_sequence = self.env['ir.sequence'].sudo().create(seq_vals)
        vals = self._prepare_taxdetail_seq(doc_type, period, new_sequence)
        return self.env['account.tax.detail.sequence'].create(vals)


class AccountTaxDetailSequence(models.Model):
    _name = 'account.tax.detail.sequence'
    _description = 'Keep track of Tax Detail sequences'
    _rec_name = 'period_id'

    doc_type = fields.Selection(
        [('sale', 'Sales'),
         ('purchase', 'Purchase')],
        string='Document Type',
        readonly=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
        ondelete='restrict',
    )
    number_next_actual = fields.Integer(
        string='Next Number',
        related='sequence_id.number_next_actual',
        readonly=True,
    )
