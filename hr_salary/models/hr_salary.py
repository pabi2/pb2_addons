# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class HRSalaryExpense(models.Model):
    _name = "hr.salary.expense"
    _inherit = ['mail.thread']
    _description = "Salary Expense"
    _rec_name = 'number'
    _order = "id desc"

    number = fields.Char(
        string='Number',
        default='/',
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        string='Description',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    user_id = fields.Many2one(
        'res.users',
        string='Prepared By',
        readonly=True,
        default=lambda self: self.env.user,
    )
    date = fields.Date(
        string='Date',
        index=True,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.context_today(self),
        copy=False,
    )
    date_submit = fields.Date(
        string='Submitted Date',
        index=True,
        readonly=True,
        copy=False,
    )
    submit_user_id = fields.Many2one(
        'res.users',
        string='Submited By',
        readonly=True,
        copy=False,
    )
    date_approve = fields.Date(
        string='Approved Date',
        index=True,
        readonly=True,
        copy=False,
    )
    approve_user_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', '=', 'purchase')],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['account.journal'].
        search([('type', '=', 'purchase')], limit=1)
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        related='move_id.line_id',
        string='Journal Items',
        readonly=True,
    )
    line_ids = fields.One2many(
        'hr.salary.line',
        'salary_id',
        string='Salary Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True,
    )
    note = fields.Text(
        string='Notes',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('submit', 'Submitted'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('open', 'Open'),
         ('paid', 'Paid'),
         ],
        string='Status',
        required=True,
        copy=False,
        default='draft',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    is_paid = fields.Boolean(
        string='Fully Paid',
        compute='_compute_is_paid',
        store=True,
    )

    @api.multi
    @api.depends('line_ids.amount')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum([x.amount for x in rec.line_ids])

    @api.multi
    def _validate_salary_line(self):
        """ Rules:
        - account_id must be regular and of type expense revenue
        - if expense, amount must >= 0, if revenue, amout must <= 0
        """
        errors = []
        for line in self.mapped('line_ids'):
            if line.account_id.type != 'other':
                t = _('Account %s is not of regular type')
                error = t % (line.account_id.code, )
                errors.append(error)
            report_type = line.account_id.user_type.report_type
            if report_type not in ('revenue', 'expense'):
                t = _('Account %s is not of type Profit & Loss')
                error = t % (line.account_id.code, )
                errors.append(error)
            if report_type == 'revenue' and line.amount > 0:
                t = _('For revenue account %s, amount must be negative')
                error = t % (line.account_id.code, )
                errors.append(error)
            if report_type == 'expense' and line.amount < 0:
                t = _('For expense account %s, amount must be positive')
                error = t % (line.account_id.code, )
                errors.append(error)
            if report_type == 'expense' and not line.partner_id.supplier:
                t = _('For expense account %s, partner %s must be supplier')
                error = t % (line.account_id.code, line.partner_id.name)
                errors.append(error)
            if report_type == 'revenue' and not line.partner_id.customer:
                t = _('For expense account %s, partner %s must be customer')
                error = t % (line.account_id.code, line.partner_id.name)
                errors.append(error)
        if errors:
            message = '\n'.join(x for x in errors)
            if len(message) > 1000:
                message = message[:1000] + '......'
            raise ValidationError(message)
        else:
            return True

    @api.multi
    def action_cancel_hook(self, moves=False):
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            moves.button_cancel()
            moves.unlink()
        return

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].\
                next_by_code('hr.salary.expense')
        return super(HRSalaryExpense, self).create(vals)

    @api.multi
    def unlink(self):
        if self.filtered(lambda l: l.state != 'draft'):
            raise ValidationError(_('You can only delete draft document'))
        return super(HRSalaryExpense, self).unlink()

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_cancel(self):
        moves = self.mapped('move_id')
        self.action_cancel_hook(moves)
        return True

    @api.multi
    def action_submit(self):
        self._validate_salary_line()
        self.write({'state': 'submit',
                    'date_submit': fields.Date.context_today(self),
                    'submit_user_id': self.env.user.id})
        return True

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve',
                    'date_approve': fields.Date.context_today(self),
                    'approve_user_id': self.env.user.id})
        return True

    @api.multi
    def action_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def action_open(self):
        self.action_move_create()
        self.write({'state': 'open'})
        return True

    @api.multi
    def action_paid(self):
        self.write({'state': 'paid'})
        return True

    @api.multi
    def action_move_create(self):
        """ Main function that is called when trying to create the
        accounting entries related to an salary expense """
        AccountMove = self.env['account.move']
        for salary in self:
            move_dict = salary._prepare_move()
            move_lines = salary._prepare_move_lines()
            move_dict.update({'line_id': move_lines})
            move = AccountMove.create(move_dict)
            salary.write({'state': 'open', 'move_id': move.id})
        return True

    @api.multi
    def _prepare_move(self):
        self.ensure_one()
        AccountMove = self.env['account.move']
        vals = AccountMove.account_move_prepare(self.journal_id.id,
                                                date=self.date,
                                                ref=self.name)
        return vals

    @api.multi
    def _prepare_move_lines(self):
        self.ensure_one()
        move_line_dict = []
        for line in self.line_ids:
            # Src
            src_line = self.move_line_get_item(line)  # Expense line
            move_line_dict.append((0, 0, self.line_get_convert(src_line)))
            # Dest
            dest_line = src_line.copy()
            dest_line['type'] = 'dest'
            move_line_dict.append((0, 0, self.line_get_convert(dest_line)))
        return move_line_dict

    @api.model
    def move_line_get_item(self, line):
        return {
            'type': 'src',
            'date': line.date,
            'name': line.name or '/',
            'partner_id': line.partner_id.id,
            'price': line.amount,
            'account_id': line.account_id.id,
            'analytic_account_id': line.analytic_account_id.id,
        }

    @api.model
    def line_get_convert(self, line):
        partner = self.env['res.partner'].browse(line['partner_id'])
        if line['type'] == 'dest':  # Receivable / Payable
            if line['price'] < 0.0:
                line['account_id'] = partner.property_account_receivable.id
            else:
                line['account_id'] = partner.property_account_payable.id
            line['price'] = - line['price']  # contra
            line['name'] = '/'
            line['analytic_account_id'] = False
        line.update({
            'date_maturity': line['date'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'ref': line.get('ref', False),
        })
        return line

    @api.multi
    @api.depends('move_id', 'move_id.line_id.reconcile_id')
    def _compute_is_paid(self):
        MoveLine = self.env['account.move.line']
        account_types = ['receivable', 'payable']
        for rec in self:
            if not rec.move_id:
                rec.is_paid = False
                continue
            # Move created, find whether all are paid.
            unreconcile_line_ids = MoveLine.search([
                ('move_id', '=', rec.move_id.id),
                ('state', '=', 'valid'),
                ('account_id.type', 'in', account_types),
                ('reconcile_id', '=', False)])._ids
            if not unreconcile_line_ids:
                rec.is_paid = True
            else:
                rec.is_paid = False

    @api.multi
    def _write(self, vals):
        """ As is_paid is triggered, so do the state """
        for rec in self:
            if 'is_paid' in vals:
                if rec.state == 'open' and vals['is_paid'] is True:
                    vals['state'] = 'paid'
                if rec.state == 'paid' and vals['is_paid'] is False:
                    vals['state'] = 'open'
        return super(HRSalaryExpense, self)._write(vals)


class HRSalaryLine(models.Model):
    _name = 'hr.salary.line'
    _description = 'Salary Line'
    _order = 'sequence, id'

    salary_id = fields.Many2one(
        'hr.salary.expense',
        string='Salary Expense',
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    name = fields.Char(
        string='Description',
    )
    date = fields.Date(
        string='Date',
        related='salary_id.date',
        store=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '=', 'other')],
        required=True,
    )
    amount = fields.Float(
        string='Amount',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
