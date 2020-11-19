# -*- coding: utf-8 -*-
from lxml import etree
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    line_item_summary = fields.Text(
        string='Items Summary',
        compute='_compute_line_item_summary',
        store=True,
        size=1000,
        help="This field provide summary of items in move line with Qty."
    )
    date = fields.Date(
        string='Posting Date',  # Rename
    )
    date_document = fields.Date(
        string='Document Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        # copy=False,
        # default=lambda self: fields.Date.context_today(self),
        compute='_compute_date_document',
        store=True,
        help="Document date follow original document's document date, "
        "otherwise, use current date",
    )
    tax_detail_ids = fields.One2many(
        'account.tax.detail',
        'ref_move_id',
        string='Tax Detail',
        readonly=False,
        copy=True,  # Add this, we want to copy it but negate amount
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        compute='_compute_validate_user_id',
    )
    state = fields.Selection(
        index=True,  # performance tuning
    )

    @api.multi
    @api.depends('document_id')
    def _compute_date_document(self):
        for rec in self:
            # Special case, clear undue VAT only
            if self._context.get('recognize_vat', False):
                date_clear_undue = self._context.get('date_clear_undue')
                rec.date_document = date_clear_undue
                continue
            # Special case, clear prepayment only
            if self._context.get('is_clear_prepaid', False):
                rec.date_document = fields.Date.context_today(self)
                continue
            # Normal case
            if rec.document_id and 'date_document' in rec.document_id:
                rec.date_document = rec.document_id.date_document
                # Cancel Case
                # if 'cancel_date_document' in rec.document_id and \
                #         rec.document_id.cancel_date_document:
                #     rec.date_document = rec.document_id.cancel_date_document
                # else:
                #     rec.date_document = rec.document_id.date_document
            else:
                if not self._context.get('direct_create'):
                    rec.date_document = fields.Date.context_today(self)

    @api.model
    def create(self, vals):
        # Special case, clear prepayment only
        if self._context.get('is_clear_prepaid', False):
            date = fields.Date.context_today(self)
            period_id = self.env['account.period'].find(dt=date).id
            vals.update({'date': date, 'period_id': period_id})
        # --
        res = super(AccountMove, self).create(vals)
        if self._context.get('direct_create'):
            res.date_document = vals.get('date_document', False)
        return res

    @api.multi
    def _compute_validate_user_id(self):
        for rec in self:
            validate_user_id = rec.create_uid
            if rec.document_id and \
               rec.document_id._name == 'interface.account.entry':
                validate_user_id = rec.document_id.validate_user_id
            rec.validate_user_id = validate_user_id

    @api.multi
    def _write(self, vals):
        # an ugly fix to prevent date_document to reset to False unattended
        if 'date_document' in vals and not vals['date_document']:
            vals.pop('date_document')
        # KV/DV
        if 'line_item_summary' in vals and vals.get('line_item_summary'):
            summary = vals.get('line_item_summary')
            self._write({'narration': summary})
        return super(AccountMove, self)._write(vals)

    @api.multi
    @api.depends('line_id.name')
    def _compute_line_item_summary(self):
        for rec in self:
            lines = rec.line_id.filtered(
                lambda l: l.name != '/'
                # and account_id.user_type.report_type in ('income', 'expense')
            )
            items = [x.name for x in lines]
            items = list(set(items))
            if items:
                rec.line_item_summary = ", ".join(items)[:1000]

    @api.model
    def _switch_move_dict_dr_cr(self, move_dict):
        """ If tax detail is copied, also negate amount """
        move_dict = super(AccountMove, self)._switch_move_dict_dr_cr(move_dict)
        tax_details = move_dict.get('tax_detail_ids', [])
        for detail in tax_details:
            detail[2]['base'] = -detail[2]['base']
            detail[2]['amount'] = -detail[2]['amount']
        move_dict['tax_detail_ids'] = tax_details
        return move_dict

    @api.multi
    def _move_reversal(self, reversal_date,
                       reversal_period_id=False, reversal_journal_id=False,
                       move_prefix=False, move_line_prefix=False):
        """ This ensure that for manual reversal, negate amount """
        self.ensure_one()
        reversal_move_id = super(AccountMove, self)._move_reversal(
            reversal_date, reversal_period_id=reversal_period_id,
            reversal_journal_id=reversal_journal_id, move_prefix=move_prefix,
            move_line_prefix=move_line_prefix
        )
        reversal_move = self.browse(reversal_move_id)
        # Negat base and amount in Tax Detail
        for tax_detail in reversal_move.tax_detail_ids:
            tax_detail.write({'base': -tax_detail.base,
                              'base_company': -tax_detail.base_company,
                              'amount': -tax_detail.amount,
                              'amount_company': -tax_detail.amount_company,
                              })
        return reversal_move_id


class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread']

    type = fields.Selection(
        index=True,
    )
    is_require_activity = fields.Boolean(
        string='Require AG&A',
    )
    #track_history
    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    user_type = fields.Many2one(track_visibility='onchange')
    asset_profile_id = fields.Many2one(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    centralized = fields.Boolean(track_visibility='onchange')
    is_require_activity = fields.Boolean(track_visibility='onchange')
    operating_unit_id = fields.Many2one(track_visibility='onchange')
    tax_ids = fields.Many2many(track_visibility='onchange')
    reconcile = fields.Boolean(track_visibility='onchange')
    currency_id = fields.Many2one(track_visibility='onchange')
    currency_mode = fields.Selection(track_visibility='onchange')
    note = fields.Text(track_visibility='onchange')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        # Option to filter only company's bank's account
        if self._context.get('company_bank_account_only', False):
            BankAcct = self.env['res.partner.bank']
            banks = BankAcct.search([
                ('state', '=', 'SA'),  # Only Saving Bank Account
                ('partner_id', '=', self.env.user.company_id.partner_id.id)])
            account_ids = \
                banks.mapped('journal_id.default_debit_account_id').ids
            args += [('id', 'in', account_ids)]
        return super(AccountAccount, self).name_search(name=name,
                                                       args=args,
                                                       operator=operator,
                                                       limit=limit)

    @api.multi
    def _check_moves(self, method):
        """ Overwrite, to remove check on inactive """
        line_obj = self.env['account.move.line']
        account_ids = self.search([('id', 'child_of', self.ids)]).ids

        if line_obj.search([('account_id', 'in', account_ids)]):
            # Overwrite, remove this check
            # if method == 'write':
            #     raise ValidationError(_('You cannot deactivate an account '
            #                             'that contains journal items.'))
            if method == 'unlink':
                raise ValidationError(_('You cannot remove an account that '
                                        'contains journal items.'))
        # Checking whether the account is set as
        # a property to any Partner or not
        values = ['account.account,%s' % (account_id,)
                  for account_id in self.ids]
        partner_prop_acc = self.env['ir.property'].search(
            [('value_reference', 'in', values)])
        if partner_prop_acc:
            raise ValidationError(_(
                'You cannot remove/deactivate an account which '
                'is set on a customer or supplier.'))
        return True


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    active = fields.Boolean(
        string='Active',
        default=True,
        help="If the active field is set to False, "
             "it will allow you to hide the journal without removing it.",
    )
    receipt = fields.Boolean(
        string='Use for Receipt',
        default=True,
        help="If checked, this journal will show only on customer payment",
    )
    payment = fields.Boolean(
        string='Use for Payment',
        default=True,
        help="If checked, this journal will show only on supplier payment",
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountJournal, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if self._context.get('default_type', False) not in ('bank', 'cash'):
            if view_type in ('tree', 'form'):
                tag = view_type == 'tree' and "/tree" or "/form"
                doc = etree.XML(res['arch'])
                nodes = doc.xpath(tag)
                for node in nodes:
                    node.set('create', 'false')
                    node.set('delete', 'false')
                res['arch'] = etree.tostring(doc)
        return res


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    revenue = fields.Boolean(
        string='Use for Revenue',
        default=True,
        help="If checked, this term will only show on SO and Cust INV",
    )
    expense = fields.Boolean(
        string='Use for Expense',
        default=True,
        help="If checked, this term will only show on PO and Sup INV",
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if 'invoice_type' in self._context:
            itype = self._context.get('invoice_type')
            if itype in ('out_invoice', 'out_refund', 'out_invoice_debitnote'):
                args += [('revenue', '=', True)]
            if itype in ('in_invoice', 'in_refund', 'in_invoice_debitnote'):
                args += [('expense', '=', True)]
        return super(AccountPaymentTerm, self).name_search(name=name,
                                                           args=args,
                                                           operator=operator,
                                                           limit=limit)
