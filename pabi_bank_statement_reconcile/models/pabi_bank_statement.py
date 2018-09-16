# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class PABIBankStatement(models.Model):
    _name = 'pabi.bank.statement'
    _description = 'This model hold bank statement generated within Odoo'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
        readonly=True,
        size=100,
        states={'draft': [('readonly', False)]},
    )
    import_file_name = fields.Char(
        string='FileName',
        size=100,
        copy=False,
    )
    import_file = fields.Binary(
        string='Import File (*.xls)',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)],
                'nstda': [('readonly', False)],
                'bank': [('readonly', False)]},
    )
    use_xlsx_template = fields.Boolean(
        string='Import template',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)],
                'nstda': [('readonly', False)],
                'bank': [('readonly', False)]},
        help="If checked, we will use the selected template for import."
        "Otherwise, simply use the standard raw template for import."
    )
    xlsx_template_id = fields.Many2one(
        'ir.attachment',
        string='XLSX Template',
        readonly=True,
        states={'draft': [('readonly', False)],
                'nstda': [('readonly', False)],
                'bank': [('readonly', False)]},
        domain=lambda self: self._get_template_domain(),
    )
    report_type = fields.Selection(
        [('payment_cheque', 'Unreconciled Cheque'),
         ('payment_direct', 'Unreconciled DIRECT'),
         ('payment_smart', 'Unreconciled SMART'),
         ('payment_oversea', 'Unreconciled Oversea'),
         ('bank_receipt', 'Unknown Bank Receipt'),
         ],
        string='Type of Report',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Template used to prefill the search criteria",
    )
    match_method = fields.Selection(
        [('cheque', 'Cheque Number, Amount'),
         ('document', 'Document Number, Amount'),
         ('date_value', 'Date Value, Amount')],
        string='Matching Method',
        required=False,
    )
    match_method_readonly = fields.Selection(
        [('cheque', 'Cheque Number, Amount'),
         ('document', 'Document Number, Amount'),
         ('date_value', 'Date Value, Amount')],
        string='Matching Method',
        readonly=True,
        related='match_method',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        domain=[('type', '=', 'bank'), ('intransit', '=', False)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        domain=lambda self: [('partner_id', '=',
                              self.env.user.company_id.partner_id.id)],
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    account_id = fields.Many2one(
        'account.account',
        related='journal_id.default_debit_account_id',
        string='Account',
        store=True,
        readonly=True,
    )
    doctype = fields.Selection(
        [('payment', 'Supplier Payment'),
         ('bank_receipt', 'Bank Receipt'),
         ],
        string='Doctype',
        default='payment',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    no_cancel_doc = fields.Boolean(
        string='No Cancelled Document',
        default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        help="Specified Payment Type, can be used to screen Payment Method",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART'),
         ('oversea', 'Oversea')
         ],
        string='Transfer Type',
        help="- DIRECT is transfer within same bank.\n"
        "- SMART is transfer is between different bank.\n"
        "- Oversea is transfer is from oversea.",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )
    item_ids = fields.One2many(
        'pabi.bank.statement.item',
        'statement_id',
        string='Statement Item',
        copy=False,
    )
    import_ids = fields.One2many(
        'pabi.bank.statement.import',
        'statement_id',
        string='Statement Import',
        copy=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('nstda', 'NSTDA Data'),
         ('bank', 'Bank Data'),
         ('reconcile', 'Reconciled'),
         ('cancel', 'Cancelled'),
         ('done', 'Done'),
         ],
        string='Status',
        default='draft',
        required=True,
    )
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Bank Statement name must be unique!')
    ]

    @api.model
    def _get_template_domain(self):
        directory = self.env.ref('pabi_bank_statement_reconcile.'
                                 'dir_statement_reconcile_template')
        return [('parent_id', '=', directory.id)]

    @api.multi
    @api.constrains('report_type', 'journal_id', 'partner_bank_id', 'state')
    def _check_wip_statement(self):
        """ Make sure that, only 1 in work in process statement is allowed
            Make sure that, when state != 'draft', all 3 fields is required """
        for rec in self:
            if rec.state == 'reconcile':
                if not (rec.report_type and rec.journal_id
                        and rec.partner_bank_id):
                    raise ValidationError(
                        _('Missing Report Type, Payment Method '
                          'or Bank Account'))
            # Find statement of the same type and journal that is in WIP state
            wip_statements = self.search([
                ('report_type', '=', rec.report_type),
                ('journal_id', '=', rec.journal_id.id),
                ('state', 'not in', ('done', 'cancel'))])
            if len(wip_statements) > 1:
                names = [x.name for x in wip_statements]
                names.pop()
                raise ValidationError(
                    _('Working on more than 1 statement of the same type '
                      'is not allowed.\n%s still open.') % ', '.join(names))

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            name = self.env['ir.sequence'].get('pabi.bank.statement')
            vals.update({'name': name})
        rec = super(PABIBankStatement, self).create(vals)
        return rec

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """ This method simply help setting default search criteia """
        if self.report_type == 'payment_cheque':
            self.match_method = 'cheque'
            self.doctype = 'payment'
            self.payment_type = 'cheque'
            self.transfer_type = False
        elif self.report_type == 'payment_direct':
            self.match_method = 'document'
            self.doctype = 'payment'
            self.payment_type = 'transfer'
            self.transfer_type = 'direct'
        elif self.report_type == 'payment_smart':
            self.match_method = 'document'
            self.doctype = 'payment'
            self.payment_type = 'transfer'
            self.transfer_type = 'smart'
        elif self.report_type == 'payment_oversea':
            self.match_method = 'document'
            self.doctype = 'payment'
            self.payment_type = 'transfer'
            self.transfer_type = 'oversea'
        elif self.report_type == 'bank_receipt':
            self.match_method = 'date_value'
            self.doctype = 'bank_receipt'
            self.payment_type = False
            self.transfer_type = False
        else:
            self.doctype = False
            self.payment_type = False
            self.transfer_type = False

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.partner_bank_id = False
        BankAcct = self.env['res.partner.bank']
        if self.journal_id:
            banks = False
            if self.doctype in ('bank_receipt', 'payment_oversea'):
                banks = BankAcct.search(
                    [('journal_id', '=', self.journal_id.id),
                     ('state', '=', 'SA')])
                if not banks:
                    raise ValidationError(_('No SA account for Payment Method '
                                            '%s') % self.journal_id.name)
            elif self.doctype:  # Doctype selected, but not the above
                banks = BankAcct.search(
                    [('journal_id', '=', self.journal_id.id),
                     ('state', '=', 'CA')])
                if not banks:
                    raise ValidationError(_('No CA account for Payment Method '
                                            '%s') % self.journal_id.name)
            self.partner_bank_id = banks and banks[0] or False

    @api.onchange('doctype')
    def _onchange_doctype(self):
        self.journal_id = False

    @api.multi
    def _prepare_move_items(self, move_lines):
        self.ensure_one()
        res = []
        for line in move_lines:
            date1 = fields.Date.from_string(self.date_report)
            date2 = fields.Date.from_string(line.date_value)
            diff_days = (date1 - date2).days
            cheque_number = line.document_id and \
                'number_cheque' in line.document_id._fields and \
                line.document_id.number_cheque
            validate_user_id = line.document_id and \
                'validate_user_id' in line.document_id._fields and \
                line.document_id.validate_user_id.id
            line_dict = {
                'move_line_id': line.id,
                'document': line.document,
                'partner_id': line.partner_id.id,
                'partner_code': line.partner_id.search_key,
                'partner_name': line.partner_id.name,
                'cheque_number': cheque_number,
                'date_value': line.date_value,
                'days_outstanding': diff_days,
                'debit': line.debit,
                'credit': line.credit,
                'validate_user_id': validate_user_id,
            }
            res.append((0, 0, line_dict))
        return res

    @api.multi
    def action_get_statement(self):
        MoveLine = self.env['account.move.line']
        for rec in self:
            rec.item_ids.unlink()
            if not self._context.get('call_from_xlsx_import', False):
                rec.import_ids.unlink()
            # Primary filter, only PV not previously matched.
            domain = [('match_import_id', '=', False),
                      ('journal_id', '=', rec.journal_id.id),
                      ('account_id', '=', rec.account_id.id)]
            if rec.doctype:
                domain.append(('doctype', '=', rec.doctype))
            move_lines = MoveLine.search(domain)
            # Secondary filter by payment_type, transfer_type
            if rec.payment_type == 'cheque':
                move_lines = move_lines.filtered(
                    lambda l: l.document_id.payment_type == 'cheque')
            elif rec.payment_type == 'transfer':
                move_lines = move_lines.filtered(
                    lambda l: l.document_id.payment_type == 'transfer' and
                    l.document_id.transfer_type == rec.transfer_type)
            if rec.doctype and rec.no_cancel_doc:
                move_lines = move_lines.filtered(
                    lambda l: l.document_id.state != 'cancel')
            # --
            rec.write({'item_ids': rec._prepare_move_items(move_lines)})
        self.write({'state': 'nstda'})
        return

    @api.multi
    def action_import_xls(self):
        for rec in self:
            rec.import_ids.unlink()
            if not rec.import_file:
                continue
            if not rec.use_xlsx_template:
                # Use raw import file, import directly to import_ids
                self.env['pabi.utils.xls'].import_xls(
                    'pabi.bank.statement.import', rec.import_file,
                    extra_columns=[('statement_id/.id', rec.id)],
                    auto_id=True)
            else:
                self.env['import.xlsx.template'].import_template(
                    rec.import_file, rec.xlsx_template_id,
                    'pabi.bank.statement', rec.id)
        self.write({'state': 'bank'})
        return

    @api.multi
    def _get_match_criteria(self):
        self.ensure_one()
        match_criteria = False
        if self.match_method == 'cheque':
            # Match by cheque number and amount
            match_criteria = """
                item.cheque_number = import.cheque_number
                and ((item.debit > 0 and item.debit = import.credit) or
                    (item.credit > 0 and item.credit = import.debit))
            """
        elif self.match_method == 'document':
            # Match by document nubmer (PV) and amount
            match_criteria = """
                item.document = import.document
                and ((item.debit > 0 and item.debit = import.credit) or
                    (item.credit > 0 and item.credit = import.debit))
            """
        elif self.match_method == 'date_value':
            # Match by document nubmer (PV) and amount
            match_criteria = """
                item.date_value = import.date_value
                and ((item.debit > 0 and item.debit = import.credit) or
                    (item.credit > 0 and item.credit = import.debit))
            """
        return match_criteria

    @api.multi
    def action_reconcile(self):
        for rec in self:
            # Clear old matching
            rec.item_ids.write({'match_import_id': False})
            rec.item_ids.mapped('move_line_id').\
                write({'match_import_id': False})  # on move line
            rec.import_ids.write({'match_import_id': False})
            match_criteria = rec._get_match_criteria()
            if not match_criteria:
                raise ValidationError(_('No Reconcile Patter found!'))
            # Update Book (items)
            rec._cr.execute("""
                update pabi_bank_statement_item book set match_import_id =
                (select import.id
                from pabi_bank_statement_item item join
                pabi_bank_statement_import import on %s
                where item.id = book.id
                and item.statement_id = %s and import.statement_id = %s
                limit 1)
                where statement_id = %s
            """ % (match_criteria, rec.id, rec.id, rec.id))
            # Update move line's match_item_id
            rec._cr.execute("""
                update account_move_line move set match_import_id =
                (select item.match_import_id
                from account_move_line move2 join
                pabi_bank_statement_item item on item.move_line_id = move2.id
                where move.id = move2.id
                and item.statement_id = %s
                limit 1)
                where id in (select move_line_id
                             from pabi_bank_statement_item
                             where statement_id = %s)
            """ % (rec.id, rec.id))
            # Update Bank (import), based on what already matched
            rec._cr.execute("""
                update pabi_bank_statement_import bank set match_item_id =
                (select item.id
                from pabi_bank_statement_item item
                where item.match_import_id = bank.id
                and statement_id = %s
                limit 1)
                where statement_id = %s
            """ % (rec.id, rec.id))

            # Finally, if some line was matched before in other statement
            rec._cr.execute("""
                update pabi_bank_statement_import new
                set prev_match_statement_id =
                (select statement_id
                from pabi_bank_statement_import old
                where old.debit = new.debit and old.credit = new.credit
                and (old.document = new.document
                     or old.cheque_number = new.cheque_number)
                and old.match_item_id is not null
                limit 1)
                where match_item_id is null
                and statement_id = %s
            """ % (rec.id, ))
        self.write({'state': 'reconcile'})
        return

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.item_ids.unlink()
            rec.import_ids.unlink()
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def post_xlsx_import_statement(self):
        """ Called from xlsx_import to automate,
        1) Complete header data 2) Get NSTDA statement 3) Reconcile """
        for rec in self:
            # 1) Header
            rec._onchange_report_type()
            rec._onchange_journal_id()
            # 2) action_get_statement
            rec.with_context(call_from_xlsx_import=True).action_get_statement()
            # 3) action_reconcile
            rec.action_reconcile()


class PABIBankStatementItem(models.Model):
    _name = 'pabi.bank.statement.item'
    _order = 'date_value, document, cheque_number'

    statement_id = fields.Many2one(
        'pabi.bank.statement',
        string='Statement ID',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        size=100,
        readonly=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        size=100,
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner Name',
        size=500,
        readonly=True,
    )
    date_value = fields.Date(
        string='Value Date',
        readonly=True,
    )
    days_outstanding = fields.Integer(
        string='Outstanding Days',
        readonly=True,
    )
    cheque_number = fields.Char(
        string='Cheque',
        size=100,
        readonly=True,
    )
    debit = fields.Float(
        string='Debit',
        readonly=True,
    )
    credit = fields.Float(
        string='Credit',
        readonly=True,
    )
    match_import_id = fields.Many2one(
        'pabi.bank.statement.import',
        string='Matched ID',
        ondelete='set null',
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
    )


class PABIBankStatementImport(models.Model):
    _name = 'pabi.bank.statement.import'
    _order = 'date_value, document, cheque_number'

    statement_id = fields.Many2one(
        'pabi.bank.statement',
        string='Statement ID',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        size=100,
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        size=100,
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner Name',
        size=100,
        readonly=True,
    )
    description = fields.Char(
        string='Description',
        size=500,
        readonly=True,
    )
    batch_code = fields.Char(
        string='Batch Code',
        size=100,
        readonly=True,
    )
    date_value = fields.Date(
        string='Value Date',
        readonly=True,
    )
    cheque_number = fields.Char(
        string='Cheque',
        size=100,
        readonly=True,
    )
    debit = fields.Float(
        string='Debit',
        readonly=True,
    )
    credit = fields.Float(
        string='Credit',
        readonly=True,
    )
    match_item_id = fields.Many2one(
        'pabi.bank.statement.item',
        string='Matched ID',
        ondelete='set null',
    )
    prev_match_statement_id = fields.Many2one(
        'pabi.bank.statement',
        string='Matched Previously',
        ondelete='set null',
    )
