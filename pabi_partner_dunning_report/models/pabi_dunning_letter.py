# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PABIDunningLetter(models.Model):
    _name = 'pabi.dunning.letter'
    _rec_name = 'number'

    number = fields.Char(
        string='Number',
    )
    date_letter = fields.Date(
        string='Letter Date'
    )
    letter_type = fields.Selection(
        [('l1', 'Overdue 7 Days'),
         ('l2', 'Overdue 14 Days'),
         ('l3', 'Overdue 19 Days')],
        string='Type',
        required=True,
    )
    date_run = fields.Date(
        string='Run Date',
        required=True,
    )
    to_whom_title = fields.Char(
        string='To Whom',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    ref_contracts = fields.Char(
        string='Ref Contracts',
        compute='_compute_ref_contracts',  # Test only
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
    )
    line_ids = fields.One2many(
        'pabi.dunning.letter.line',
        'letter_id',
        string='Dunning Lines'
    )
    # Printing Text
    letter_header = fields.Text(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )
    letter_footer = fields.Text(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )
    letter_signature = fields.Text(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )

    @api.multi
    @api.depends()
    def _compute_amount_total(self):
        for letter in self:
            amount_total = sum(letter.line_ids.mapped('amount_residual'))
            letter.amount_total = amount_total

    @api.multi
    @api.depends()
    def _compute_ref_contracts(self):
        """ TODO: TEST ONLY, will be revised again with myContract """
        for letter in self:
            letter.ref_contracts = 'Contract 1, Contract 2'

    @api.model
    def _eval_text(self, text, obj):
        template = self.env['email.template']
        return template.render_template(text, obj._name, obj.id)

    @api.multi
    @api.depends()
    def _compute_letter_text(self):
        company = self.env['res.company'].search([])[0]
        for letter in self:
            if letter.letter_type == 'l1':
                letter.letter_header = \
                    self._eval_text(company.letter1_header, letter)
                letter.letter_footer = \
                    self._eval_text(company.letter1_footer, letter)
                letter.letter_signature = \
                    self._eval_text(company.letter1_signature, letter)
            if letter.letter_type == 'l2':
                letter.letter_header = \
                    self._eval_text(company.letter2_header, letter)
                letter.letter_footer = \
                    self._eval_text(company.letter2_footer, letter)
                letter.letter_signature = \
                    self._eval_text(company.letter2_signature, letter)
            if letter.letter_type == 'l3':
                letter.letter_header = \
                    self._eval_text(company.letter3_header, letter)
                letter.letter_footer = \
                    self._eval_text(company.letter3_footer, letter)
                letter.letter_signature = \
                    self._eval_text(company.letter3_signature, letter)


class PABIDunningLetterLine(models.Model):
    _name = 'pabi.dunning.letter.line'

    letter_id = fields.Many2one(
        'pabi.dunning.letter',
        string='Dunning Letter',
        index=True,
        ondelete='cascade',
    )
    letter_type = fields.Selection(
        [('l1', 'Overdue 7 Days'),
         ('l2', 'Overdue 14 Days'),
         ('l3', 'Overdue 19 Days')],
        related='letter_id.letter_type',
        string='Type',
        store=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Invoice',
    )
    date_invoice = fields.Date(
        related='move_line_id.date',
        string='Invoice Date',
        store=True,
    )
    date_run = fields.Date(
        related='letter_id.date_run',
        string='Date Run',
        store=True,
    )
    date_due = fields.Date(
        related='move_line_id.date_maturity',
        string='Date Due',
        store=True,
    )
    amount_residual = fields.Float(
        string='Balance',
        compute='_compute_amount_residual',
        store=True,
    )
    _sql_constraints = [
        ('line_uniq', 'UNIQUE(move_line_id, date_run)',
         'Dunning Line unique constraint error!'),
    ]

    @api.multi
    @api.depends('move_line_id')
    def _compute_amount_residual(self):
        for line in self:
            line.amount_residual = line.move_line_id.amount_residual
