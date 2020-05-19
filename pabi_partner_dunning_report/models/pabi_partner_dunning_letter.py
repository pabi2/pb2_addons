# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.tools.amount_to_text_en import amount_to_text
from pychart.arrow import default


class PABIPartnerDunningLetter(models.Model):
    _name = 'pabi.partner.dunning.letter'
    _rec_name = 'number'

    number = fields.Char(
        string='Number',
        size=500,
    )
    create_uid = fields.Many2one(
        'res.users',
        string='Creator',
        readonly=True,
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
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_letter_text',
        readonly=True,
    )
    date_run = fields.Date(
        string='Run Date',
        required=True,
    )
    to_whom_title = fields.Char(
        string='To Whom',
        size=500,
        default='ผศจ. ผ่าน ผอ.ฝ่ายบริหารธุรกิจอุทยานวิทยาศาสตร์ประเทศไทย'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    subject = fields.Char(
        string='Subject',
        compute='_compute_letter_text',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
    )
    amount_total_text_en = fields.Char(
        string='Total Amount Text',
        compute='_compute_amount_total',
    )
    line_ids = fields.One2many(
        'pabi.partner.dunning.letter.line',
        'letter_id',
        string='Dunning Lines'
    )
    # Printing Text
    letter_header = fields.Html(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )
    letter_footer = fields.Html(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )
    letter_signature = fields.Html(
        string='Header',
        compute='_compute_letter_text',
        readonly=True,
    )
    config_id = fields.Many2one(
        'pabi.dunning.config',
        'Dunning Config',
        compute='_compute_config_id',
    )
    
    @api.multi
    def _compute_config_id(self):
        for config in self:
            config.config_id = self.env.ref('pabi_partner_dunning_report.pabi_dunning_config_data').id
    
    @api.model
    def create(self, vals):
        #vals['config_id'] = self.env.ref('pabi_partner_dunning_report.pabi_dunning_config_data').id
        return super(PABIPartnerDunningLetter, self).create(vals)
        

    @api.multi
    def _compute_amount_total(self):
        for letter in self:
            self._cr.execute("""
                select sum(amount_residual)
                from pabi_partner_dunning_letter_line
                where letter_id = %s
            """, (letter.id,))
            letter.amount_total = self._cr.fetchone()[0]
            letter.amount_total_text_en = amount_to_text(
                letter.amount_total, 'en', 'Baht').replace(
                    'and Zero Cent', 'Only').replace(
                        'Cent', 'Satang').replace('Cents', 'Satang')

    @api.model
    def _eval_text(self, text, obj):
        template = self.env['email.template']
        return template.render_template(text, obj._name, obj.id)

    @api.multi
    def _compute_letter_text(self):
        company = self.env['res.company'].search([])[0]
        for letter in self:
            move_line = letter.line_ids and \
                letter.line_ids[0].move_line_id or False
            letter.currency_id = move_line and move_line.currency_id or \
                self.env.user.company_id.currency_id
            if letter.letter_type == 'l1':
                letter.subject = letter.config_id.letter1_subject
                letter.letter_header = \
                    self._eval_text(letter.config_id.letter1_header, letter)
                letter.letter_footer = \
                    self._eval_text(letter.config_id.letter1_footer, letter)
                letter.letter_signature = \
                    self._eval_text(letter.config_id.letter1_signature, letter)
            if letter.letter_type == 'l2':
                letter.subject = letter.config_id.letter2_subject
                letter.letter_header = \
                    self._eval_text(letter.config_id.letter2_header, letter)
                letter.letter_footer = \
                    self._eval_text(letter.config_id.letter2_footer, letter)
                letter.letter_signature = \
                    self._eval_text(letter.config_id.letter2_signature, letter)
            if letter.letter_type == 'l3':
                letter.subject = letter.config_id.letter3_subject
                letter.letter_header = \
                    self._eval_text(letter.config_id.letter3_header, letter)
                letter.letter_footer = \
                    self._eval_text(letter.config_id.letter3_footer, letter)
                letter.letter_signature = \
                    self._eval_text(letter.config_id.letter3_signature, letter)

    @api.multi
    def get_dunning_letter_line(self, lines):
        if not lines:
            return []
        where = ''
        if len(lines) == 1:
            where += ' dl.id = %s' % (str(lines.ids[0]), )
        else:
            where += ' dl.id in %s' % (str(tuple(lines.ids)), )
        self._cr.execute("""
            select ml.ref, dl.date_invoice, dl.date_due,
                   sum(dl.amount_residual)
            from pabi_partner_dunning_letter_line dl
            join account_move_line ml on dl.move_line_id = ml.id
            where %s
            group by ml.ref, dl.date_invoice, dl.date_due
            order by ml.ref, dl.date_invoice, dl.date_due
            """ % (where, ))
        return self._cr.fetchall()


class PABIPartnerDunningLetterLine(models.Model):
    _name = 'pabi.partner.dunning.letter.line'

    letter_id = fields.Many2one(
        'pabi.partner.dunning.letter',
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
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validator',
        compute='_compute_validate_user_id',
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
        #related='move_line_id.date_maturity',
        compute='_compute_date_due',
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
    def _compute_date_due(self):
        for line in self:
            line.date_due = line.move_line_id.date_maturity

    @api.multi
    @api.depends('move_line_id')
    def _compute_amount_residual(self):
        for line in self:
            move_line = line.move_line_id
            sign = move_line.debit - move_line.credit < 0 and -1 or 1
            line.amount_residual = sign * abs(move_line.amount_residual)
            
    @api.multi
    @api.depends('move_line_id')
    def _compute_validate_user_id(self):
        for line in self:
            ref_name = line.move_line_id.move_id.name
            if self.env["interface.account.entry"].sudo().search([('number','=',ref_name)]):
                interface_account = self.env["interface.account.entry"].sudo().search([('number','=',ref_name)]).validate_user_id
            elif self.env["account.invoice"].sudo().search([('number','=',ref_name)]):
                interface_account = self.env["account.invoice"].sudo().search([('number','=',ref_name)]).validate_user_id
            else:
                interface_account = line.move_line_id.move_id.write_uid
            validate_user = interface_account
            line.validate_user_id = validate_user