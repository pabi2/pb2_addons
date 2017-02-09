# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PABIBankStatement(models.Model):
    _name = 'pabi.bank.statement'
    _description = 'This model hold bank statement generated within Odoo'

    name = fields.Char(
        string='Name',
        default='/',
        required=True,
    )
    import_file = fields.Binary(
        string='Import File',
    )
    doctype = fields.Selection(
        [('payment', 'Payment'),
         ('receipt', 'Receipt'),
         ],
        string='Doctype',
        required=True,
        default='payment',
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        required=True,
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
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', '=', 'bank')]
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        compute='_compute_account_id',
        store=True,
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )
    item_ids = fields.One2many(
        'pabi.bank.statement.item',
        'statement_id',
        string='Statement Item',
    )
    import_ids = fields.One2many(
        'pabi.bank.statement.import',
        'statement_id',
        string='Statement Import',
    )

    @api.multi
    @api.depends('journal_id')
    def _compute_account_id(self):
        for rec in self:
            if rec.journal_id.default_debit_account_id != \
                    rec.journal_id.default_credit_account_id:
                rec.account_id = False
            else:
                rec.account_id = rec.journal_id.default_debit_account_id

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        self.transfer_type = False

    @api.model
    def _prepare_move_items(self, move_lines):
        res = []
        for line in move_lines:
            line_dict = {
                'move_line_id': line.id,
                'document': line.document,
                'partner_id': line.partner_id.id,
                'partner_code': line.partner_id.search_key,
                'partner_name': line.partner_id.name,
                'cheque_number': line.document_id.number_cheque,
                'debit': line.debit,
                'credit': line.credit,
            }
            res.append((0, 0, line_dict))
        return res

    @api.multi
    def action_get_statement(self):
        MoveLine = self.env['account.move.line']
        for rec in self:
            rec.item_ids.unlink()
            search_domain = [
                ('journal_id', '=', rec.journal_id.id),
                ('account_id', '=', rec.account_id.id),
                ('doctype', '=', rec.doctype),
                ('date_value', '>=', rec.date_from),
                ('date_value', '<=', rec.date_to),
                ]
            move_lines = MoveLine.search(search_domain)
            # Filtered by payment_type, transfer_type
            if rec.payment_type == 'cheque':
                move_lines = move_lines.filtered(
                    lambda l: l.document_id.payment_type == 'cheque')
            elif rec.payment_type == 'transfer':
                move_lines = move_lines.filtered(
                    lambda l: l.document_id.payment_type == 'transfer' and
                    l.document_id.transfer_type == rec.transfer_type)
            # --
            rec.write({'item_ids': self._prepare_move_items(move_lines)})
        return

class PABIBankStatementItem(models.Model):
    _name = 'pabi.bank.statement.item'

    statement_id = fields.Many2one(
        'pabi.bank.statement',
        string='Statement ID',
        index=True,
        ondelete='cascade',
    )
    document = fields.Char(
        string='Document',
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    partner_code = fields.Char(
        string='Partner Code',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    cheque_number = fields.Char(
        string='Cheque',
    )
    debit = fields.Float(
        string='Debit',
    )
    credit = fields.Float(
        string='Credit',
    )
    match_import_id = fields.Many2one(
        'pabi.bank.statement.import',
        string='Matched ID',
    )


class PABIBankStatementImport(models.Model):
    _name = 'pabi.bank.statement.import'

    statement_id = fields.Many2one(
        'pabi.bank.statement',
        string='Statement ID',
        index=True,
        ondelete='cascade',
    )
    document = fields.Char(
        string='Document',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    partner_code = fields.Char(
        string='Partner Code',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    cheque_number = fields.Char(
        string='Cheque',
    )
    debit = fields.Float(
        string='Debit',
    )
    credit = fields.Float(
        string='Credit',
    )
    match_item_id = fields.Many2one(
        'pabi.bank.statement.item',
        string='Matched ID',
    )
