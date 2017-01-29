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
    line_ids = fields.One2many(
        'pabi.dunning.letter.line',
        'letter_id',
        string='Dunning Lines'
    )


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
