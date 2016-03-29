# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _debitnote_cleanup_lines(self, lines):
        """Convert records to dict of values suitable for one2many
        line creation
            :param list(browse_record) lines: records to convert
            :return: list of command tuple for one2many line creation
            [(0, 0, dict of valueis), ...]
        """
        clean_lines = []
        for line in lines:
            clean_line = {}
            for field in line._all_columns.keys():
                if line._all_columns[field].column._type == 'many2one':
                    clean_line[field] = line[field].id
                elif line._all_columns[field].column._type not in ['many2many',
                                                                   'one2many',
                                                                   ]:
                    clean_line[field] = line[field]
                elif field == 'invoice_line_tax_id':
                    tax_list = []
                    for tax in line[field]:
                        tax_list.append(tax.id)
                    clean_line[field] = [(6, 0, tax_list)]
            clean_lines.append(clean_line)
        return map(lambda x: (0, 0, x), clean_lines)

    @api.model
    def _prepare_debitnote(self, invoice, date=None,
                           period_id=None, description=None,
                           journal_id=None):
        """Prepare the dict of values to create the new debit note
            from the invoice.
            This method may be overridden to implement custom
            debit note generation (making sure to call super() to establish
            a clean extension chain).

            :param integer invoice_id: id of the invoice to create debit note
            :param dict invoice: read of the invoice to create debit note
            :param string date: debit note creation date from the wizard
            :param integer period_id: force account.period from the wizard
            :param string description: description of
            the debit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the debit note
        """
        obj_journal = self.env['account.journal']

        type_list = ['out_invoice', 'in_invoice', ]
        if invoice.type not in type_list:
            raise UserError(_('Can not create Debit Note from this document!'))

        invoice_data = {}
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id',
                      'company_id', 'account_id', 'currency_id',
                      'payment_term', 'user_id', 'fiscal_position', ]:
            if invoice._all_columns[field].column._type == 'many2one':
                invoice_data[field] = invoice[field].id
            else:
                if invoice[field]:
                    invoice_data[field] = invoice[field]
                else:
                    invoice_data[field] = False
#                 invoice_data[field] =
#                 invoice[field] if invoice[field] else False

        invoice_lines = self._debitnote_cleanup_lines(invoice.invoice_line)

        tax_lines = filter(lambda l: l['manual'], invoice.tax_line)
        tax_lines = self._debitnote_cleanup_lines(tax_lines)
        if journal_id:
            debitnote_journal_ids = [journal_id]
        elif invoice['type'] == 'in_invoice':
            debitnote_journal_ids = obj_journal.search(
                [('type', '=', 'purchase_debitnote')]).ids
        else:
            debitnote_journal_ids = obj_journal.search(
                [('type', '=', 'sale_debitnote')]).ids

        if not date:
            date = time.strftime('%Y-%m-%d')

        if debitnote_journal_ids:
            debitnote_journal_ids = debitnote_journal_ids[0]
        else:
            debitnote_journal_ids = False
        invoice_data.update({
            'type': invoice['type'],
            'date_invoice': date,
            'state': 'draft',
            'number': False,
            'invoice_line': invoice_lines,
            'tax_line': tax_lines,
            'journal_id': debitnote_journal_ids,
            'origin_invoice_id': invoice.id
        })
        if period_id:
            invoice_data['period_id'] = period_id
        if description:
            invoice_data['name'] = description
        return invoice_data

    @api.multi
    def debitnote(self, date=None, period_id=None,
                  description=None, journal_id=None):
        new_ids = []
        for invoice in self:
            invoice = self._prepare_debitnote(invoice, date=date,
                                              period_id=period_id,
                                              description=description,
                                              journal_id=journal_id,
                                              )
            # create the new invoice
            new_ids.append(self.create(invoice))
#         for new_invoice in self.browse(cr, uid, new_ids, context=context):
#             if new_invoice.invoice_id_ref:
#                 self.write(cr, uid, [new_invoice.invoice_id_ref.id]
#         {'invoice_id_ref': new_invoice.id})
        return new_ids

    is_debitnote = fields.Boolean(
        compute="_compute_is_debitnote",
        string='Debit Note',
        store=True,
        )
    origin_invoice_id = fields.Many2one(
        'account.invoice',
        string='Origin invoice',
        readonly=True,
        states={'draft': [('readonly', False)]},
        )
    debited_amount = fields.Float(
        compute='_compute_debited_amount',
        string='Debited Amount',
        digits_compute=dp.get_precision('Product Price'),
        )
    debit_invoice_ids = fields.One2many(
        'account.invoice',
        'origin_invoice_id',
        'Debit Documents',
        domain=[('type', '=', 'out_invoice')],
        readonly=True,
        copy=False,
        )

    @api.multi
    @api.depends('journal_id', 'journal_id.type')
    def _compute_is_debitnote(self):
        for invoice in self:
            if invoice.journal_id and invoice.journal_id.type in (
                    'sale_debitnote', 'purchase_debitnote'):
                invoice.is_debitnote = True
            else:
                invoice.is_debitnote = False

    @api.multi
    @api.depends('refund_invoice_ids',
                 'refunded_amount',
                 'refund_invoice_ids.state',
                 'refund_invoice_ids.amount_untaxed')
    def _compute_debited_amount(self):
        for invoice in self:
            # Get the refund based on this invoice
            refund_ids = self.search([('origin_invoice_id', '=', invoice.id),
                                      ('type', '=', 'out_invoice'),
                                      ('state', '!=', ('cancel'))])
            refunded_amount = sum([r.amount_untaxed for r in refund_ids])
            invoice.debited_amount = refunded_amount

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu
            )
        journal_obj = self.env['account.journal']
        type = self.env.context.get('journal_type', False)
        for field in res['fields']:
            if field == 'journal_id' and type in ('sale', 'purchase'):
                # Add debit note type with sale type.
                if type == 'sale':
                    type = ('sale', 'sale_debitnote')
                if type == 'purchase':
                    type = ('purchase', 'purchase_debitnote')
                journal_select = journal_obj._name_search(
                    '', [('type', 'in', type)], limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res
