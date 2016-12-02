# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class InterfaceAccountEntry(models.Model):
    _name = 'interface.account.entry'
    _inherit = ['mail.thread']
    _description = 'Interface to create accounting entry, invoice and payment'

    system_id = fields.Many2one(
        'interface.system',
        string='System Origin',
        ondelete='restrict',
        required=True,
        help="System where this interface transaction is being called",
    )
    action_id = fields.Many2one(
        'interface.action',
        string='Action',
        ondelete='restrict',
        required=True,
        help="Action that this interface will do, journal will depend on it",
    )
    name = fields.Char(
        string='Document Origin',
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        related='action_id.journal_id',
        store=True,
        readonly=True,
        copy=False,
        help="Journal to be used in creating Journal Entry",
    )
    line_ids = fields.One2many(
        'interface.account.entry.line',
        'interface_id',
        string='Lines',
        copy=True,
    )
    legend = fields.Text(
        string='Legend',
        readonly=True,
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
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        index=True,
        readonly=True,
        default='draft',
        track_visibility='onchange',
        copy=False,
    )

    # ================== Main Execution Method ==================
    @api.multi
    def execute(self):
        res = {}
        invoice_entry = self.env.ref('pabi_interface.action_invoice_entry')
        # payment_entry = self.env.ref('pabi_interface.action_payment_entry')
        for interface in self:
            # Action = Create Invoice JE
            if interface.action_id == invoice_entry:
                move = interface._action_invoice_entry()
                res.update({interface.name: move.name})
            # Action = Create Payment JE
            # if interface.action_id == payment_entry:

            # Action = Reverse JE

        return res

    # ================== Sub Method by Action ==================
    @api.model
    def _action_invoice_entry(self):
        self._validate_invoice_entry()
        move = self._create_journal_entry()
        move.post()
        return move

    # == Validate by Action ==
    @api.model
    def _validate_invoice_entry(self):
        self._check_journal()
        self._check_has_line()
        self._check_tax_line()
        self._check_line_dimension()
        self._check_posting_date()
        self._check_date_maturity()
        self._check_amount_currency()

    # @api.model
    # def _validate_payment_entry(self):

    # == Validation Logics ==
    @api.model
    def _check_journal(self):
        if not self.journal_id:
            raise ValidationError(
                _('Journal has not been setup for this Action!'))

    @api.model
    def _check_has_line(self):
        if len(self.line_ids) == 0:
            raise ValidationError(_('Document must have lines!'))

    @api.model
    def _check_has_no_line(self):
        if len(self.line_ids) > 0:
            raise ValidationError(_('Document must has no lines!'))

    @api.model
    def _check_tax_line(self):
        tax_lines = self.line_ids.filtered('tax_id')
        for line in tax_lines:
            if line.tax_id.account_collected_id != line.account_id:
                raise ValidationError(
                    _("Invaid Tax Account Code\n%s's account code should be "
                      "%s") % (line.tax_id.account_collected_id.code))
            if not line.taxbranch_id:
                raise ValidationError(_('No tax branch for tax line'))
            if not line.tax_invoice_number:
                raise ValidationError(_('No tax invoice number for tax line'))

    @api.model
    def _check_line_dimension(self):
        # All line must have same OU
        operating_unit = list(set(self.line_ids.mapped('operating_unit_id')))
        if len(operating_unit) != 1:
            raise ValidationError(
                _('Same operating Unit must be set for all lines!'))
        # All line must have account id
        account_ids = [x.account_id.id for x in self.line_ids]
        if False in account_ids:
            raise ValidationError(_('Alll lines must have account code!'))
        # For account non asset/liability line must have section/project
        for line in self.line_ids:
            report_type = line.account_id.user_type.report_type
            if report_type not in ('asset', 'liability'):
                if not line.section_id and not line.project_id:
                    raise ValidationError(
                        _('%s is non-banlance sheet item, it requires '
                          'Section/Project') % (line.account_id.code,))
                if not line.activity_id or not line.activity_group_id:
                    raise ValidationError(
                        _('%s is non-banlance sheet item, it requires '
                          'Activity Group and Activity') %
                        (line.account_id.code,))
            else:
                if line.section_id or line.project_id:
                    raise ValidationError(
                        _('%s is banlance sheet item, it do not require AG/A '
                          'or Section/Project') % (line.account_id.code,))
        for line in self.line_ids:
            if line.activity_id and \
                    line.activity_id.account_id != line.account_id:
                raise ValidationError(
                    _('%s does not belong to activity %s') %
                    (line.account_id.code, line.activity_id.name))

    @api.model
    def _check_posting_date(self):
        # All line has same posting date
        move_dates = list(set(self.line_ids.mapped('date')))
        if len(move_dates) > 1:
            raise ValidationError(
                _('Inteferce lines should not have different posting date!'))

    @api.model
    def _check_date_maturity(self):
        # For account.type receivable and payble, must have date maturity
        lines = self.line_ids.filtered(
            lambda l: l.account_id.type in ('payable', 'receivable'))
        dates = [x.date_maturity for x in lines]
        if False in dates:
            raise ValidationError(
                _('Payable or receivabe lines must have payment due date!'))

    @api.model
    def _check_amount_currency(self):
        # For non THB, must have amount_currency
        lines = self.line_ids.filtered(
            lambda l: l.currency_id and
            l.currency_id.id != self.company_id.currency_id)
        for l in lines:
            if (l.debit or l.credit) and not l.amount_currency:
                raise ValidationError(
                    _('Amount Currency must not be False '))

    # == Execution Logics ==
    @api.model
    def _create_journal_entry(self):
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        Analytic = self.env['account.analytic.account']
        TaxDetail = self.env['account.tax.detail']
        Period = self.env['account.period']

        move_date = self.line_ids[0].date
        ctx = self._context.copy()
        ctx.update({'company_id': self.company_id.id})
        periods = Period.find(dt=move_date)
        period_id = periods and periods[0].id or False
        journal = self.journal_id
        ctx.update({
            'journal_id': journal.id,
            'period_id': period_id,
        })
        move = AccountMove.create({
            'ref': self.name,
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
            }

            move_line = AccountMoveLine.with_context(ctx).create(vals)
            # Update dimension & analytic
            move_line.update_related_dimension(vals)
            analytic_account = Analytic.create_matched_analytic(move_line)
            move_line.analytic_account_id = analytic_account.id
            # --
            if analytic_account and not journal.analytic_journal_id:
                raise ValidationError(
                    _("You have to define an analytic journal on the "
                      "'%s' journal!") % (journal.name,))

            # For Tax Line, also add to account_tax_detail
            if line.tax_id:
                tax_dict = TaxDetail._prepare_tax_detail_dict(
                    False, False,  # No invoice_tax_id, voucher_tax_id
                    self._get_doc_type(journal),
                    line.partner_id.id, line.tax_invoice_number,
                    line.date, line.tax_base_amount, line.debit or line.credit)
                tax_dict['tax_id'] = line.tax_id.id
                detail = TaxDetail.create(tax_dict)
                detail._set_next_sequence()
            # --

        self.write({'move_id': move.id,
                    'state': 'done'})
        return move

    @api.model
    def _get_doc_type(self, journal):
        doc_type = False  # Determine doctype based on journal type
        if journal.type in ('sale', 'sale_refund', 'sale_debitnote'):
            doc_type = 'sale'
        elif journal.type in \
                ('purchase', 'purchase_refund', 'purchase_debitnote'):
            doc_type = 'purchase'
        else:
            raise ValidationError(
                _("The selected journal type is not supported: %s") %
                (journal.name,))
        return doc_type

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
        required=True,
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
