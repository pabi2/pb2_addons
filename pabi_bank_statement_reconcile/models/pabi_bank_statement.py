# -*- coding: utf-8 -*-
import base64
import os
import xlrd
import unicodecsv
from datetime import datetime

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class PABIBankStatement(models.Model):
    _name = 'pabi.bank.statement'
    _description = 'This model hold bank statement generated within Odoo'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
    )
    import_file = fields.Binary(
        string='Import File (*.csv)',
        copy=False,
    )
    import_file_xls = fields.Binary(
        string='Import File (*.xls)',
        copy=False,
    )
    report_type = fields.Selection(
        [('payment_cheque', 'Unreconciled Cheque'),
         ('payment_direct', 'Unreconciled DIRECT'),
         ('payment_smart', 'Unreconciled SMART'),
         ('bank_receipt', 'Unknown Bank Receipt'),
         ],
        string='Type of Report',
        required=True,
        help="Template used to prefill the search criteria",
    )
    match_method = fields.Selection(
        [('cheque', 'Cheque Number, Amount'),
         ('document', 'Document Number, Amount'),
         ('date_value', 'Date Value, Amount')],
        string='Matching Method',
        required=True,
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
        domain=[('type', '=', 'bank')],
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
    )
    doctype = fields.Selection(
        [('payment', 'Supplier Payment'),
         ('bank_receipt', 'Bank Receipt'),
         ],
        string='Doctype',
        default='payment',
    )
    no_cancel_doc = fields.Boolean(
        string='No Cancelled Document',
        default=True,
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART')
         ],
        string='Transfer Type',
        help="- DIRECT is transfer within same bank.\n"
        "- SMART is transfer is between different bank."
    )
    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
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
    import_error = fields.Text(
        string='Import Errors',
        readonly=True,
    )
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Bank Statement name must be unique!')
    ]

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
        if self.journal_id.default_debit_account_id != \
                self.journal_id.default_credit_account_id:
            self.account_id = False
        else:
            self.account_id = self.journal_id.default_debit_account_id

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
            rec.import_error = False
            # Primary filter
            domain = [('date_value', '>=', rec.date_from),
                      ('date_value', '<=', rec.date_to), ]
            if rec.journal_id:
                domain.append(('journal_id', '=', rec.journal_id.id))
            if rec.account_id:
                domain.append(('account_id', '=', rec.account_id.id))
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
        return

    @api.model
    def _add_statement_id_column(self, statement_id, file_txt):
        i = 0
        txt_lines = []
        for line in file_txt.split('\n'):
            if line and i == 0:
                line = '"statement_id/.id",' + line
            elif line:
                line = str(statement_id) + ',' + line
            txt_lines.append(line)
            i += 1
        file_txt = '\n'.join(txt_lines)
        return file_txt

    @api.multi
    def action_import_xls(self):
        _TEMPLATE_FIELDS = ['statement_id/.id',
                            'document',
                            'cheque_number',
                            'description',
                            'debit', 'credit',
                            'date_value',
                            'batch_code']
        for rec in self:
            rec.import_ids.unlink()
            rec.import_error = False
            decoded_data = base64.decodestring(rec.import_file_xls)
            randms = datetime.utcnow().strftime('%H%M%S%f')[:-3]
            f = open('temp' + randms + '.xls', 'wb+')
            f.write(decoded_data)
            f.seek(0)
            f.close()
            wb = xlrd.open_workbook(f.name)
            st = wb.sheet_by_index(0)
            csv_file = open('temp' + randms + '.csv', 'wb')
            csv_out = unicodecsv.writer(csv_file,
                                        encoding='utf-8',
                                        quoting=unicodecsv.QUOTE_ALL)
            for rownum in xrange(st.nrows):
                if rownum > 0:
                    row_values = st.row_values(rownum)
                    if st.cell(rownum, 5).value:
                        str_date = datetime.fromtimestamp(
                            st.cell(rownum, 5).value / 1e3).strftime("%Y-%m-%d")
                        row_values[5] = str_date
                    csv_out.writerow(row_values)
                else:
                    csv_out.writerow(st.row_values(rownum))
            csv_file.close()
            csv_file = open('temp' + randms + '.csv', 'r')
            file_txt = csv_file.read()
            csv_file.close()
            os.unlink('temp' + randms + '.xls')
            os.unlink('temp' + randms + '.csv')
            if not file_txt:
                continue
            Import = self.env['base_import.import']
            file_txt = self._add_statement_id_column(rec.id, file_txt)
            imp = Import.create({
                'res_model': 'pabi.bank.statement.import',
                'file': file_txt,
            })
            [errors] = imp.do(
                _TEMPLATE_FIELDS,
                {'headers': True, 'separator': ',',
                 'quoting': '"', 'encoding': 'utf-8'})
            if errors:
                rec.import_error = str(errors)

    @api.multi
    def action_import_csv(self):
        _TEMPLATE_FIELDS = ['statement_id/.id',
                            'document',
                            'cheque_number',
                            'description',
                            'debit', 'credit',
                            'date_value',
                            'batch_code']
        for rec in self:
            rec.import_ids.unlink()
            rec.import_error = False
            if not rec.import_file:
                continue
            Import = self.env['base_import.import']
            file_txt = base64.decodestring(rec.import_file)
            file_txt = self._add_statement_id_column(rec.id, file_txt)
            imp = Import.create({
                'res_model': 'pabi.bank.statement.import',
                'file': file_txt,
            })
            [errors] = imp.do(
                _TEMPLATE_FIELDS,
                {'headers': True, 'separator': ',',
                 'quoting': '"', 'encoding': 'utf-8'})
            if errors:
                rec.import_error = str(errors)

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
                item.date_vallue = import.date_vallue
                and ((item.debit > 0 and item.debit = import.credit) or
                    (item.credit > 0 and item.credit = import.debit))
            """
        return match_criteria

    @api.multi
    def action_reconcile(self):
        for rec in self:
            # Clear old matching
            rec.item_ids.write({'match_import_id': False})
            rec.import_ids.write({'match_item_id': False})
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
        return

    # @api.multi
    # def action_import_and_reconcile(self):
    #     self.action_get_statement()
    #     self.action_import_csv()
    #     self.action_reconcile()


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
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner Name',
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
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner Name',
        readonly=True,
    )
    description = fields.Char(
        string='Description',
        readonly=True,
    )
    batch_code = fields.Char(
        string='Batch Code',
        readonly=True,
    )
    date_value = fields.Date(
        string='Value Date',
        readonly=True,
    )
    cheque_number = fields.Char(
        string='Cheque',
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
