# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        selection_add=[('internal', 'Internal Charge')],
    )
    internal_section_id = fields.Many2one(
        'res.section',
        string='Internal Section',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    internal_project_id = fields.Many2one(
        'res.project',
        string='Internal Project',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group_id',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    rev_ic_journal_id = fields.Many2one(
        'account.journal',
        string='Revenue Internal Charge Journal',
        compute='_compute_internal_charge_journal',
        store=True,
    )
    exp_ic_journal_id = fields.Many2one(
        'account.journal',
        string='Expense Internal Charge Journal',
        compute='_compute_internal_charge_journal',
        store=True,
    )
    rev_ic_move_id = fields.Many2one(
        'account.move',
        string='Internal Revenue Journal Entry',
        readonly=True,
        copy=False,
    )
    exp_ic_move_id = fields.Many2one(
        'account.move',
        string='Internal Expense Journal Entry',
        readonly=True,
        copy=False,
    )

    @api.onchange('internal_project_id')
    def _onchange_internal_project_id(self):
        self.internal_section_id = False

    @api.onchange('internal_section_id')
    def _onchange_internal_section_id(self):
        self.internal_project_id = False

    @api.multi
    @api.depends('pay_to')
    def _compute_internal_charge_journal(self):
        for rec in self:
            if rec.pay_to == 'internal':
                rec.rev_ic_journal_id = \
                    rec.env.ref('pabi_budget_internal_charge.rev_ic_journal')
                rec.exp_ic_journal_id = \
                    rec.env.ref('pabi_budget_internal_charge.exp_ic_journal')
            else:
                rec.rev_ic_journal_id = False
                rec.exp_ic_journal_id = False

    @api.one
    @api.constrains('pay_to')
    def _check_pay_to_internal_charge(self):
        if self.pay_to == 'internal':
            if self.is_employee_advance or self.is_advance_clearing:
                raise ValidationError(_('Only Expense can be Interal Charge!'))
            if not self.rev_ic_journal_id or not self.exp_ic_journal_id or \
                    not self.rev_ic_journal_id.default_debit_account_id or \
                    not self.exp_ic_journal_id.default_credit_account_id:
                raise ValidationError(
                    _('Internal Charge Journal has not been setup properly!\n'
                      'Make sure default account is Internal Charge account'))
            if not self.internal_section_id and not self.internal_project_id:
                raise ValidationError(
                    _('No Project/Section selected on Internal Charge'))
            for line in self.line_ids:
                if not line.section_id and not line.project_id:
                    raise ValidationError(
                        _('No Project/Section selected on expense line'))

    @api.multi
    @api.depends('activity_id')
    def _compute_activity_group_id(self):
        for rec in self:
            rec.activity_group_id = rec.activity_id.activity_group_ids and \
                rec.activity_id.activity_group_ids[0] or False

    @api.model
    def _is_valid_for_invoice(self):
        res = super(HRExpense, self)._is_valid_for_invoice()
        if self.pay_to == 'internal':  # Do not create invoice for IC
            raise ValidationError(
                _('For internal charge, it is not allowed to create invoice'))
        return res

    @api.model
    def _prepare_move(self, expense, journal, period):
        # The Internal Charge journal must consume budget
        if not journal.analytic_journal_id:
            raise UserError(
                _("You have to define an analytic journal on "
                  "the '%s' journal!") %
                (journal.name, ))
        vals = {
            'operating_unit_id': expense.operating_unit_id.id,
            'ref': expense.name,
            'period_id': period.id,
            'journal_id': journal.id,
            'date': expense.date
        }
        return vals

    @api.model
    def _prepare_move_line(self, move, expense_line, analytic_account,
                           activity, debit=0.0, credit=0.0):
        if not activity.account_id:
            raise UserError(
               _("You have to define an account code on "
                 "the '%s' activity!") % (activity.name, ))
        vals = {
            'operating_unit_id': move.operating_unit_id.id,
            'move_id': move.id,
            'journal_id': move.journal_id.id,
            'period_id': move.period_id.id,
            'analytic_account_id': analytic_account.id,
            'name': expense_line.name,
            'quantity': 1.0,
            'debit': debit,
            'credit': credit,
            'account_id': activity.account_id.id,
            'partner_id': False,
            'date': move.date,
            'date_maturity': move.date
        }
        return vals

    @api.multi
    def create_internal_charge_move(self):
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        Analytic = self.env['account.analytic.account']
        Expense = self.env['hr.expense.line']
        Period = self.env['account.period']
        for expense in self:
            ctx = self._context.copy()
            ctx.update({'company_id': expense.company_id.id})
            periods = Period.find(expense.date)
            period = periods and periods[0] or False
            ctx.update({'period_id': period.id})

            # ============== Create 1st JE for Revenue ==============
            # Cr: Revenue
            rev_journal = expense.rev_ic_journal_id
            ctx.update({'journal_id': rev_journal.id})
            # move header
            rev_move_vals = self._prepare_move(expense, rev_journal, period)
            rev_move = AccountMove.create(rev_move_vals)
            temp_exp_line = Expense.create({
                'expense_id': expense.id,
                'project_id': expense.internal_project_id.id,
                'section_id': expense.internal_section_id.id,
                'activity_id': expense.activity_id.id,
                'activity_group_id': expense.activity_group_id.id,
                'name': expense.name,
            })
            temp_exp_line.update_related_dimension(rev_move_vals)
            analytic_account = Analytic.create_matched_analytic(temp_exp_line)
            rev_cr_vals = self._prepare_move_line(rev_move,
                                                  temp_exp_line,
                                                  analytic_account,
                                                  expense.activity_id,
                                                  debit=0.0,
                                                  credit=expense.amount)
            # Copy before dimensions filled
            rev_dr_vals = rev_cr_vals.copy()

            AccountMoveLine.with_context(ctx).create(rev_cr_vals)
            # Dr: Internal Charge
            rev_dr_vals.update({
                'move_id': rev_move.id,
                'analytic_account_id': False,
                'debit': rev_cr_vals['credit'],
                'credit': False,
                'account_id': rev_journal.default_debit_account_id.id
            })
            print rev_dr_vals
            AccountMoveLine.with_context(ctx).create(rev_dr_vals)
            temp_exp_line.unlink()

            # ============== Create 2nd JE for Expense ==============
            exp_journal = expense.exp_ic_journal_id
            ctx.update({'journal_id': exp_journal.id})
            # move header
            exp_move_vals = self._prepare_move(expense, exp_journal, period)
            exp_move = AccountMove.create(exp_move_vals)
            # Debit each expense line
            for line in expense.line_ids:
                analytic_account = Analytic.create_matched_analytic(line)
                exp_dr_vals = self._prepare_move_line(exp_move, line,
                                                      analytic_account,
                                                      line.activity_id,
                                                      debit=line.total_amount,
                                                      credit=0.0)
                AccountMoveLine.with_context(ctx).create(exp_dr_vals)

            # Cr: Internal Charge (equel to Dr: Internal Charge)
            exp_cr_vals = rev_dr_vals.copy()
            exp_cr_vals.update({
                'move_id': exp_move.id,
                'analytic_account_id': False,
                'debit': False,
                'credit': rev_dr_vals['debit'],
                'account_id': exp_journal.default_credit_account_id.id
            })
            print exp_cr_vals
            AccountMoveLine.with_context(ctx).create(exp_cr_vals)

            expense.write({'rev_ic_move_id': rev_move.id,
                           'exp_ic_move_id': exp_move.id})
