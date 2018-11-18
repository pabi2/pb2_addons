# -*- coding: utf-8 -*-
import logging
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare

SALE_JOURNAL = ['sale', 'sale_refund', 'sale_debitnote']
PURCHASE_JOURNAL = ['purchase', 'purchase_refund', 'purchase_debitnote']
BANK_CASH = ['bank', 'cash']

_logger = logging.getLogger(__name__)


class InterfaceAccountEntry(models.Model):
    _name = 'interface.account.entry'
    _rec_name = 'number'
    _inherit = ['mail.thread']
    _description = 'Interface to create accounting entry, invoice and payment'
    _order = 'id desc'

    system_id = fields.Many2one(
        'interface.system',
        string='System Origin',
        ondelete='restrict',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="System where this interface transaction is being called",
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    number = fields.Char(
        string='Number',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default="/",
        copy=False,
        size=500,
    )
    name = fields.Char(
        string='Document Origin',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default="/",
        copy=False,
        size=500,
    )
    type = fields.Selection(
        [('invoice', 'Invoice'),
         ('voucher', 'Payment'),
         ('reverse', 'Reverse')],
        string='Type',
        readonly=True,
        index=True,
    )
    charge_type = fields.Selection(  # Prepare for pabi_internal_charge
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the move line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
        help="Journal to be used in creating Journal Entry",
    )
    # Move to line level
    # contract_number = fields.Char(
    #     string='Contract Number',
    #     size=500,
    # )
    # contract_date_start = fields.Date(
    #     string='Contract Start Date',
    # )
    # contract_date_end = fields.Date(
    #     string='Contract Start End',
    # )
    to_reconcile = fields.Boolean(
        string='To Reconcile',
        compute='_compute_to_reconcile',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        related='line_ids.partner_id',
        readonly=True,
    )
    line_ids = fields.One2many(
        'interface.account.entry.line',
        'interface_id',
        string='Lines',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        'res.company',
        related='journal_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
        index=True,
    )
    to_reverse_entry_id = fields.Many2one(
        'interface.account.entry',
        string='To Reverse',
        domain=[('state', '=', 'done'), ('to_reverse_entry_id', '=', False)],
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    reversed_date = fields.Date(
        string='Reversed Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        index=True,
        default='draft',
        track_visibility='onchange',
        copy=False,
    )
    residual = fields.Float(
        string='Unreconciled Amount',
        digits=dp.get_precision('Account'),
        compute='_compute_residual',
        store=True,
        help="Remaining amount due.",
    )
    preprint_number = fields.Char(
        string='Pre-print No.',
        size=100,
    )
    cancel_reason = fields.Char(
        string='Cancel Reason',
        size=500,
    )
    to_payment = fields.Char(
        string='Payment Entries',
        compute='_compute_to_payment',
    )
    date_document = fields.Date(
        string='Document Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    _sql_constraints = [('sys_doc_unique', 'unique(name,system_id)',
                         'Document must be unique per system.')]

    @api.multi
    @api.depends('journal_id')
    def _compute_to_payment(self):
        for rec in self:
            reconcile_ids = rec.move_id.line_id.mapped('reconcile_id').ids
            inteface_reconcile_ids = rec.env['account.move.line'].search(
                [('reconcile_id', 'in', reconcile_ids)]
            )
            move_line_diff = set(inteface_reconcile_ids) \
                .difference(rec.move_id.line_id)
            diff_ids = []
            payment_name = False
            for x in move_line_diff:
                if x.move_id.name not in diff_ids:
                    diff_ids.append(x.move_id.name.encode('utf-8'))
            payment_name = ', '.join(diff_ids)
            if payment_name:
                rec.to_payment = payment_name

    @api.onchange('to_reverse_entry_id')
    def _onchange_to_reverse_entry_id(self):
        self.journal_id = self.to_reverse_entry_id.journal_id
        self.system_id = self.to_reverse_entry_id.system_id

    @api.onchange('type')
    def _onchange_type(self):
        domain = []
        if self.type == 'invoice':
            domain = [('type', 'in', SALE_JOURNAL + PURCHASE_JOURNAL)]
        if self.type == 'voucher':
            domain = [('type', 'in', BANK_CASH)]
        return {'domain': {'journal_id': domain}}

    @api.multi
    @api.depends('journal_id')
    def _compute_to_reconcile(self):
        for rec in self:
            rec.to_reconcile = rec.journal_id.type in BANK_CASH

    @api.one
    @api.depends(
        'state', 'line_ids',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    def _compute_residual(self):
        """ Use account_invoice._compute_residual() as sample """
        self.residual = 0.0
        partial_reconciliations_done = []
        for line in self.sudo().move_id.line_id:
            if line.account_id.type not in ('receivable', 'payable'):
                continue
            if line.reconcile_partial_id and line.reconcile_partial_id.id in \
                    partial_reconciliations_done:
                continue
            line_amount = line.currency_id and \
                line.amount_residual_currency or line.amount_residual
            if line.reconcile_partial_id:
                partial_reconciliations_done.append(
                    line.reconcile_partial_id.id)
            self.residual += line_amount
        self.residual = max(self.residual, 0.0)

    @api.model
    def create(self, vals):
        if not vals.get('system_id', False) and \
                vals.get('to_reverse_entry_id', False):
            reverse_entry = self.browse(vals['to_reverse_entry_id'])
            vals['system_id'] = reverse_entry.system_id.id
            vals['journal_id'] = reverse_entry.journal_id.id
        return super(InterfaceAccountEntry, self).create(vals)

    # ================== Main Execution Method ==================
    @api.model
    def _prepare_voucher_move_for_reversal(self, move):
        for line in move.line_id:
            # Similar to def voucher_cancel()
            line.refresh()
            if line.reconcile_id:
                move_line_ids = [move_line.id for move_line in
                                 line.reconcile_id.line_id]
                move_line_ids.remove(line.id)
                line.reconcile_id.unlink()
                if len(move_line_ids) >= 2:
                    move_lines = self.env['account.move.line'].\
                        browse(move_line_ids)
                    move_lines.reconcile_partial('auto')

    @api.multi
    def execute(self):
        for interface in self:
            # Set type based on journal type
            if interface.to_reverse_entry_id:
                interface.type = 'reverse'
            elif interface.journal_id.type in BANK_CASH:
                interface.type = 'voucher'
            elif interface.journal_id.type in SALE_JOURNAL + PURCHASE_JOURNAL:
                interface.type = 'invoice'
            # 1) Reverse
            if interface.type == 'reverse':
                AccountMove = self.env['account.move']
                move = interface.to_reverse_entry_id.move_id
                # For invoice, check if already paid?
                if move.journal_id.type not in ('bank', 'cash'):
                    if move.line_id.filtered(
                            lambda l:
                            (l.reconcile_id or l.reconcile_partial_id) and
                            l.account_id.reconcile):
                        raise ValidationError(
                            _('%s is already reconciled (paid)!') % move.name)
                # If payment reversal, refresh it first
                if interface.to_reverse_entry_id.type == 'voucher':
                    self._prepare_voucher_move_for_reversal(move)
                # Start reverse
                move_dict = move.copy_data({
                    'name': move.name + '_VOID',
                    'ref': move.ref, })
                move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
                rev_move = AccountMove.create(move_dict)
                accounts = move.line_id.mapped('account_id')
                for account in accounts:
                    AccountMove.\
                        _reconcile_voided_entry_by_account(
                            [move.id, rev_move.id], account.id)
                rev_move.button_validate()
                interface.write({'move_id': rev_move.id,
                                 'state': 'done'})
                interface.number = rev_move.name
            # 2) Invoice / Refund
            elif interface.type == 'invoice':
                move = interface._action_invoice_entry()
                interface.number = move.name
                # self._update_account_move_line_ref(move)
                self._update_account_move_line_origin(move)
            # 3) Payment Receipt
            elif interface.type == 'voucher':
                move = interface._action_payment_entry()
                interface.number = move.name
                # self._update_account_move_line_ref(move)
                self._update_account_move_line_origin(move)
        return True

    # ================== Sub Method by Action ==================
    # @api.model
    # def _update_account_move_line_ref(self, move):
    #     self._cr.execute("""
    #         update account_move_line ml set ref = (
    #             select ref from interface_account_entry_line
    #             where ref_move_line_id = ml.id)
    #         where move_id = %s
    #     """, (move.id, ))
    #     return True

    @api.model
    def _update_account_move_line_origin(self, move):
        self._cr.execute("""
            update account_move_line ml set origin = (
                select ref from interface_account_entry
                where move_id = ml.move_id)
            where move_id = %s
        """, (move.id, ))
        return True

    @api.multi
    def _action_invoice_entry(self):
        self.ensure_one()
        self._validate_invoice_entry()
        move = self._create_journal_entry()
        return move

    @api.multi
    def _action_payment_entry(self):
        self.ensure_one()
        self._validate_payment_entry()
        move = self._create_journal_entry()
        self._reconcile_payment()
        return move

    # == Validate by Action ==
    @api.multi
    def _validate_invoice_entry(self):
        self.ensure_one()
        Checker = self.env['interface.account.checker']
        Checker._check_balance_entry(self)
        Checker._check_journal(self)
        Checker._check_has_line(self)
        Checker._check_tax_line(self)
        Checker._check_line_normal(self)
        Checker._check_line_dimension(self)
        Checker._check_posting_date(self)
        Checker._check_date_maturity(self)
        Checker._check_amount_currency(self)

    # @api.model
    @api.multi
    def _validate_payment_entry(self):
        self.ensure_one()
        Checker = self.env['interface.account.checker']
        Checker._check_balance_entry(self)
        Checker._check_journal(self)
        Checker._check_has_line(self)
        Checker._check_tax_line(self)
        Checker._check_line_normal(self)
        Checker._check_line_dimension(self)
        Checker._check_posting_date(self)
        Checker._check_invoice_to_reconcile(self)
        Checker._check_amount_currency(self)
        Checker._check_select_reconcile_with(self)

    # == Execution Logics ==
    @api.model
    def _create_journal_entry(self):
        if self.move_id:
            raise ValidationError(_('Journal Entry is already created'))

        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        Analytic = self.env['account.analytic.account']
        TaxDetail = self.env['account.tax.detail']
        Period = self.env['account.period']

        move_date = self.line_ids[0].date
        operating_unit_id = self.line_ids[0].operating_unit_id.id
        ctx = self._context.copy()
        ctx.update({'company_id': self.company_id.id})
        periods = Period.find(dt=move_date)
        period = periods and periods[0] or False
        period_id = period and period.id or False
        journal = self.journal_id
        ctx.update({
            'journal_id': journal.id,
            'period_id': period_id,
            'fiscalyear_id': period and period.fiscalyear_id.id or False,
        })
        move_name = "/"
        if journal.sequence_id:
            self = self.with_context(ctx)
            sequence_id = journal.sequence_id.id
            move_name = self.env['ir.sequence'].next_by_id(sequence_id)
        else:
            raise ValidationError(
                _('Please define a sequence on the journal.'))
        move = AccountMove.create({
            'name': move_name,
            'system_id': self.system_id.id,
            'ref': self.name,
            'operating_unit_id': operating_unit_id,
            'period_id': period_id,
            'journal_id': journal.id,
            'date': move_date,
        })
        # Prepare Move Line
        for line in self.line_ids:
            vals = {
                'ref': self.name,
                'operating_unit_id': line.operating_unit_id.id,
                'move_id': move.id,
                'journal_id': journal.id,
                'period_id': period_id,
                # Line Info
                'name': line.name,
                'debit': line.debit,
                'credit': line.credit,
                'account_id': line.account_id.id,
                'partner_id': line.partner_id.id,
                'date': line.date,
                'date_maturity': line.date_maturity,   # Payment Due Date
                # Dimensions
                'activity_group_id': line.activity_group_id.id,
                'activity_id': line.activity_id.id,
                'section_id': line.section_id.id,
                'project_id': line.project_id.id,
                # For Tax
                'taxbranch_id': line.taxbranch_id.id,
                # Charge type
                'charge_type': self.charge_type or 'expense'  # Default to exp
            }
            move_line = AccountMoveLine.with_context(ctx).create(vals)
            line.ref_move_line_id = move_line
            # For balance sheet item, do not need dimension (kittiu: ignore)
            # report_type = line.account_id.user_type.report_type
            # if report_type not in ('asset', 'liability'):
            move_line.update_related_dimension(vals)
            if move_line.taxbranch_id:  # Has dimension
                analytic_account = Analytic.create_matched_analytic(move_line)
                move_line.analytic_account_id = analytic_account
            # kittiu: This throw error in some case, so temp remove it.
            # if analytic_account and not journal.analytic_journal_id:
            #     raise ValidationError(
            #         _("You have to define an analytic journal on the "
            #           "'%s' journal!") % (journal.name,))

            # For Normal Tax Line, also add to account_tax_detail
            if line.tax_id and not line.tax_id.is_wht and \
                    not line.tax_id.is_undue_tax:
                # Set negative tax for refund
                sign = 1
                if journal.type in SALE_JOURNAL + PURCHASE_JOURNAL:  # invoice
                    if journal.type in ('sale_refund', 'purchase_refund'):
                        sign = -1
                if journal.type in BANK_CASH:  # Payment
                    if line.tax_id.type_tax_use == 'sale':
                        sign = line.credit and 1 or -1
                tax_dict = TaxDetail._prepare_tax_detail_dict(
                    False, False,  # No invoice_tax_id, voucher_tax_id
                    self._get_doc_type(journal, line),
                    line.partner_id.id, line.tax_invoice_number, line.date,
                    sign * line.tax_base_amount,
                    sign * (line.debit or line.credit),
                    move_line_id=move_line.id,  # created by move line
                )
                tax_dict['tax_id'] = line.tax_id.id
                tax_dict['taxbranch_id'] = line.taxbranch_id.id
                detail = TaxDetail.create(tax_dict)
                detail._set_next_sequence()
            # --

        self.write({'move_id': move.id,
                    'state': 'done'})
        return move

    @api.model
    def _get_doc_type(self, journal, line):
        doc_type = False  # Determine doctype based on journal type
        if journal.type in SALE_JOURNAL:
            doc_type = 'sale'
        elif journal.type in PURCHASE_JOURNAL:
            doc_type = 'purchase'
        elif journal.type in BANK_CASH:
            doc_type = line.tax_id.type_tax_use  # sale/purchase
        else:
            raise ValidationError(
                _("The selected journal type is not supported: %s") %
                (journal.name,))
        return doc_type

    @api.multi
    def _reconcile_payment(self):
        self.ensure_one()
        # To reconcile each reciable/payable line
        to_reconcile_lines = self.line_ids.filtered('account_id.reconcile')
        #  .filtered(lambda l: l.account_id.type in ('receivable', 'payable'))
        for line in to_reconcile_lines:
            payment_ml = line.ref_move_line_id
            invoice_ml = line.reconcile_move_line_ids
            # Validate Account
            # if payment_ml.account_id != invoice_ml.account_id:
            #     raise ValidationError(
            #         _("Wrong account to reconcile for line '%s'.\nInvoice "
            #           "move line account not equal to that of payment") %
            #         (line.name,))
            # Validate Amount Sign
            # NOTE: remove this condition for case Undue Tax
            # psign = (payment_ml.debit - payment_ml.credit) > 0 and 1 or -1
            # isign = (invoice_ml.debit - invoice_ml.credit) > 0 and 1 or -1
            # if psign == isign:
            #     raise ValidationError(
            #         _("To reconcile, amount should be in opposite Dr/Cr "
            #           "for line '%s'") % (line.name,))
            # Full or Partial reconcile

            # lines = payment_ml | invoice_ml
            # residual = sum([x.debit - x.credit for x in lines])
            # # Reconcile Full or Partial
            # if not residual:
            #     lines.reconcile('manual')
            # else:
            #     lines.reconcile_partial('manual')

            # to_rec = move_lines.filtered(lambda l: l.account_id == account)
            to_rec = payment_ml | invoice_ml
            # If nohting to reconcile
            debit = sum(to_rec.mapped('debit'))
            credit = sum(to_rec.mapped('credit'))
            if debit == 0.0 or credit == 0.0:
                continue
            # --
            if len(to_rec) >= 2:
                if debit != credit:
                    to_rec.reconcile_partial('auto')
                else:
                    to_rec.reconcile('auto')

    # ==========================================================
    #                  INTERFACE OTHER SYSEM
    # ==========================================================

    @api.multi
    def test_generate_interface_account_entry(self):
        data_dict = {
            'name': u'Test Interface Account Entry from web',
            'number': u'/',
            'system_id': u'PABI2',
            'type': u'invoice',
            'journal_id': u'Sales Journal',
            'partner_id': u'Kaushik',
            'line_ids': [
                {
                    'name': u'Credit Line',
                    'tax_id': False,
                    'tax_invoice_number': False,
                    'tax_base_amount': 0.0,
                    # Line Info
                    'debit': 428.0,
                    'credit': 0.0,
                    'account_id': u'ลูกหนี้การค้า',
                    'amount_currency': 400.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': False,
                    'activity_id': False,
                    'section_id': False,
                    'project_id': False,
                    'taxbranch_id': False,
                    'date': u'2017-01-13',
                    'date_maturity': u'2017-01-14',
                },
                {
                    'name': u'Debit Line-1',
                    'tax_id': u'Undue Output VAT 7%',
                    'tax_invoice_number': u'IV16001',
                    'tax_base_amount': 400.0,
                    # Line Info
                    'debit': 0.0,
                    'credit': 28.0,
                    'account_id': u'พักภาษีขาย',
                    'amount_currency': 28.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': False,
                    'activity_id': False,
                    'section_id': False,
                    'project_id': False,
                    'taxbranch_id': u'ศูนย์เทคโนโลยีโลหะและวัสดุแห่งชาติ',
                    'date': u'2017-01-13',
                    'date_maturity': u'',
                },
                {
                    'name': u'Debit Line-2',
                    'tax_id': False,
                    'tax_invoice_number': u'IV16001',
                    'tax_base_amount': 0.0,
                    # Line Info
                    'debit': 0.0,
                    'credit': 400.0,
                    'account_id': u'วิเคราะห์ทดสอบ/สอบเทียบ/ใบรับรองคุณภาพ',
                    'amount_currency': 400.0,
                    'currency_id': u'THB',
                    'partner_id': u'Kaushik',
                    'operating_unit_id': u'ศว.',
                    'activity_group_id': u'ค่าวิเคราะห์และทดสอบ',
                    'activity_id': u'ให้บริการวิเคราะห์ทดสอบ/ร่วมวิจัย/'
                    u'รับจ้างวิจัย/เครื่องมือวัด/สอบเทียบ/ใบรับรองคุณภาพ',
                    'section_id': u'Procurement Section',
                    'project_id': False,
                    'taxbranch_id': False,
                    'date': u'2017-01-13',
                    'date_maturity': u'',
                }
            ]
        }
        return self.generate_interface_account_entry(data_dict)

    @api.model
    def _pre_process_interface_account_entry(self, data_dict):
        return data_dict

    @api.model
    def generate_interface_account_entry(self, data_dict):
        _logger.info("IA - Input: %s" % data_dict)
        try:
            data_dict = self._pre_process_interface_account_entry(data_dict)
            # For migration period, payment reconicle can be entry or item
            # so, we need to manually check it
            Move = self.env['account.move']
            for l in data_dict.get('line_ids', []):
                if not l.get('reconcile_move_id', False):
                    continue
                # If reconcile_move_id not found, try reconcile_move_line_ref
                vals = Move.name_search(l['reconcile_move_id'], operator='=')
                if len(vals) != 1:
                    # Auto reassign to reconcile_move_line_id
                    l['reconcile_move_line_ref'] = l['reconcile_move_id']
                    del l['reconcile_move_id']
            # -
            res = self.env['pabi.utils.ws'].create_data(self._name, data_dict)
            if res['is_success']:
                res_id = res['result']['id']
                document = self.browse(res_id)
                document.execute()
                # More info
                res['result']['number'] = document.number
                res['result']['fiscalyear'] = \
                    document.move_id.period_id.fiscalyear_id.name
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info("IA - Output: %s" % res)
        return res


class InterfaceAccountEntryLine(models.Model):
    _name = 'interface.account.entry.line'
    _order = 'sequence'

    interface_id = fields.Many2one(
        'interface.account.entry',
        string='Interface Entry',
        index=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=0,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    debit = fields.Float(
        string='Debit',
    )
    credit = fields.Float(
        string='Credit',
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
    )
    tax_invoice_number = fields.Char(
        string='Tax Invoice',
    )
    tax_base_amount = fields.Float(
        string='Tax Base',
        digits_compute=dp.get_precision('Account')
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
        ondelete='cascade',
        digits_compute=dp.get_precision('Account')
    )
    amount_currency = fields.Float(
        string='Amount Currency',
        help="The amount expressed in an optional other currency.",
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=False,
    )
    date = fields.Date(
        string='Posting Date',
        required=True,
        help="Account Posting Date. "
        "As such, all lines in the same document should have same date."
    )
    date_maturity = fields.Date(
        string='Maturity Date',
        help="Date "
    )
    # Dimensions
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
    )
    ref_move_line_id = fields.Many2one(
        'account.move.line',
        string='Ref Journal Item',
        readonly=True,
        copy=False,
    )
    reconcile_move_id = fields.Many2one(
        'account.move',
        string='Reconcile Entry',
        domain="[('state', '=', 'posted'),"
        "('partner_id', '=', partner_id)]",
        copy=False,
    )
    reconcile_move_line_ref = fields.Char(
        string='Reconcile Item Ref.',
        copy=False,
        help="For case migration only, allow direct select account.move.line",
    )
    reconcile_move_line_ids = fields.Many2many(
        'account.move.line',
        string='Reconcile with',
        compute='_compute_reconcile_move_line_ids',
        # store=True,
    )
    contract_charge_type = fields.Char(
        string='Contract Charge Type',
        help="Text information of contract",
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
    )
    # Moved from header
    contract_number = fields.Char(
        string='Contract Number',
        size=500,
    )
    contract_date_start = fields.Date(
        string='Contract Start Date',
    )
    contract_date_end = fields.Date(
        string='Contract Start End',
    )
    # --
    ref = fields.Char(
        string='Reference',
        size=500,
    )

    @api.multi
    # @api.depends('reconcile_move_id', 'reconcile_move_line_ref')
    def _compute_reconcile_move_line_ids(self):
        AccountMoveLine = self.env['account.move.line']
        for rec in self:
            if not rec.reconcile_move_id and not rec.reconcile_move_line_ref:
                continue
            dom = [('state', '=', 'valid'),
                   ('account_id', '=', rec.account_id.id),
                   ('account_id.reconcile', '=', True),
                   ('reconcile_id', '=', False)]
            if rec.reconcile_move_id:
                dom.append(('move_id', '=', rec.reconcile_move_id.id))
            elif rec.reconcile_move_line_ref:
                dom.append(('ref', '=', rec.reconcile_move_line_ref))
            move_lines = AccountMoveLine.search(dom)
            if not move_lines:
                raise ValidationError(
                    _('No valid reconcilable move line for %s, %s') %
                    ((rec.reconcile_move_line_ref or
                      rec.reconcile_move_id.name), rec.account_id.code))
            rec.reconcile_move_line_ids = move_lines
        return True


class InterfaceAccountChecker(models.AbstractModel):
    _name = 'interface.account.checker'
    _description = 'Dedicate for checking the validity of interface lines'

    @api.model
    def _check_journal(self, inf):
        if not inf.journal_id:
            raise ValidationError(
                _('Journal has not been setup for this Action!'))

    @api.model
    def _check_has_line(self, inf):
        if len(inf.line_ids) == 0:
            raise ValidationError(_('Document must have lines!'))

    @api.model
    def _check_has_no_line(self, inf):
        if len(inf.line_ids) > 0:
            raise ValidationError(_('Document must has no lines!'))

    @api.model
    def _check_tax_line(self, inf):
        # journal_type = inf.journal_id.type
        tax_lines = inf.line_ids.filtered('tax_id')
        for line in tax_lines:
            if line.tax_id.account_collected_id != line.account_id:
                raise ValidationError(
                    _("Invaid Tax Account Code\n%s's account code should be "
                      "%s") % (line.tax_id.account_collected_id.code,
                               line.account_id.code))
            if not line.taxbranch_id:
                raise ValidationError(_('No tax branch for tax line'))
            if not line.tax_invoice_number:
                raise ValidationError(_('No tax invoice number for tax line'))
            if (line.debit or line.credit) and not line.tax_base_amount:
                raise ValidationError(_('Tax Base should not be zero!'))
            # Sales, tax must be in credit and debit for refund
            # Purchase, tax must be in debit and redit for refund

            # kittiu: removed by NSTDA request
            # invalid = False
            # if journal_type in SALE_JOURNAL:
            #     if journal_type != 'sale_refund':
            #         invalid = line.debit > 0
            #     else:
            #         invalid = line.credit > 0
            # if journal_type in PURCHASE_JOURNAL:
            #     if journal_type != 'purchase_refund':
            #         invalid = line.credit > 0
            #     else:
            #         invalid = line.debit > 0
            # if invalid:
            #     raise ValidationError(
            #        _('Tax in wrong side of dr/cr as refer to journal type!'))
            # --

    @api.model
    def _check_line_normal(self, inf):
        # All line must have same OU
        # operating_unit = list(set(inf.line_ids.mapped('operating_unit_id')))
        # if len(operating_unit) != 1:
        #     raise ValidationError(
        #         _('Same operating Unit must be set for all lines!'))
        # --
        # All line must have account id
        account_ids = [x.account_id.id for x in inf.line_ids]
        if False in account_ids:
            raise ValidationError(_('Alll lines must have same account code!'))
        # All line must have same partner
        partners = inf.line_ids.mapped('partner_id')
        if partners and len(partners) > 1:
            raise ValidationError(_('Alll lines must have same partner!'))

    # @api.model
    # def _check_line_dimension(self, inf):
    #     # For account non asset/liability line must have section/project
    #     for line in inf.line_ids:
    #         report_type = line.account_id.user_type.report_type
    #         if report_type not in ('asset', 'liability'):
    #             if not line.section_id and not line.project_id:
    #                 raise ValidationError(
    #                     _('%s is non-banlance sheet item, it requires '
    #                       'Section/Project') % (line.account_id.code,))
    #             if not line.activity_id or not line.activity_group_id:
    #                 raise ValidationError(
    #                     _('%s is non-banlance sheet item, it requires '
    #                       'Activity Group and Activity') %
    #                     (line.account_id.code,))
    #         else:
    #             if line.section_id or line.project_id:
    #                 raise ValidationError(
    #                  _('%s is banlance sheet item, it do not require AG/A '
    #                       'or Section/Project') % (line.account_id.code,))
    #     for line in inf.line_ids:
    #         if line.activity_id and \
    #                 line.activity_id.account_id != line.account_id:
    #             raise ValidationError(
    #                 _('%s does not belong to activity %s') %
    #                 (line.account_id.code, line.activity_id.name))

    @api.model
    def _check_line_dimension(self, inf):
        # For product / activity line must have section/project
        for line in inf.line_ids:
            if line.activity_group_id and \
                    (line.product_id or line.activity_id):
                if not line.section_id and not line.project_id:
                    raise ValidationError(
                        _('%s requires section/project') % line.name)
            # else:
            #     if line.section_id or line.project_id:
            #         raise ValidationError(
            #             _('%s does not require section/project') % line.name)
        # Check activity account
        for line in inf.line_ids:
            if line.activity_id and \
                    line.activity_id.account_id != line.account_id:
                raise ValidationError(
                    _('%s does not belong to activity %s') %
                    (line.account_id.code, line.activity_id.name))

    @api.model
    def _check_posting_date(self, inf):
        # All line has same posting date
        move_dates = list(set(inf.line_ids.mapped('date')))
        if len(move_dates) > 1:
            raise ValidationError(
                _('Inteferce lines should not have different posting date!'))

    @api.model
    def _check_invoice_to_reconcile(self, inf):
        # For payment/receipt, receivable and payable must have Reconcile with
        if not inf.to_reconcile:
            return
        for line in inf.line_ids:
            if line.account_id.type in ('receivable', 'payable') and \
                    not line.reconcile_move_line_ids:
                raise ValidationError(
                    _("Account receivable/payable line '%s' require "
                      "an invoice to reconcile!") % (line.name,))

        move_dates = list(set(inf.line_ids.mapped('date')))
        if len(move_dates) > 1:
            raise ValidationError(
                _('Inteferce lines should not have different posting date!'))

    @api.model
    def _check_date_maturity(self, inf):
        # For account.type receivable and payble, must have date maturity
        lines = inf.line_ids.filtered(
            lambda l: l.account_id.type in ('payable', 'receivable'))
        dates = [x.date_maturity and True or False for x in lines]
        if False in dates:
            raise ValidationError(
                _('Payable or receivabe lines must have payment due date!'))
        # For non receivable and payble, must NOT have date maturity
        lines = inf.line_ids.filtered(
            lambda l: l.account_id.type not in ('payable', 'receivable'))
        dates = [x.date_maturity and True or False for x in lines]
        if True in dates:
            raise ValidationError(
                _('Non payable and non receivable lines '
                  'must not have payment due date!'))

    @api.model
    def _check_amount_currency(self, inf):
        # For non THB, must have amount_currency
        lines = inf.line_ids.filtered(
            lambda l: l.currency_id and
            l.currency_id != inf.company_id.currency_id)
        for l in lines:
            if (l.debit or l.credit) and not l.amount_currency:
                raise ValidationError(
                    _('Amount Currency must not be False '))

    @api.model
    def _check_select_reconcile_with(self, inf):
        # Either reconcile_move_id or reconcile_move_line_id can be selected
        lines = inf.line_ids.filtered(
            lambda l: l.reconcile_move_id and l.reconcile_move_line_ref)
        messages = []
        for l in lines:
            messages.append('%s-%s' % (l.sequence, l.name))
        if messages:
            raise ValidationError(_('Reconcile Entry and Reconcile Item Ref.'
                                    'can not coexists!\n%s') %
                                  ', '.join(messages))

    @api.model
    def _check_balance_entry(self, inf):
        # Validate balanced entry
        prec = self.env['decimal.precision'].precision_get('Account')
        debit = sum(inf.line_ids.mapped('debit'))
        credit = sum(inf.line_ids.mapped('credit'))
        if float_compare(debit, credit, prec) != 0:
            raise ValidationError(
                _('Interface Entry, %s, not balanced!') % inf.name)
