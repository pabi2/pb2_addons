# -*- coding: utf-8 -*-
import time
from datetime import datetime
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
    )

    @api.onchange('pay_to')
    def _onchange_pay_to(self):
        if self.pay_to == 'internal':
            self.journal_id = self.env.ref('pabi_budget_internal_charge.'
                                           'internal_charge_journal', False)
        else:
            self.journal_id = False

    @api.one
    @api.constrains('pay_to')
    def _check_pay_to_internal_charge(self):
        if self.pay_to == 'internal':
            if self.is_employee_advance or self.is_advance_clearing:
                raise ValidationError(_('Only Expense can be Interal Charge!'))

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

    @api.multi
    def create_internal_charge_move(self):
        entry = {}
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']
        period_obj = self.env['account.period']
        Analytic = self.env['account.analytic.account']
        context = self._context.copy()

        for expense in self:
            ctx = context.copy()
            ctx.update({'company_id': expense.company_id.id})
            periods = period_obj.find(expense.date)
            period = periods and periods[0] or False
            ctx.update({'journal_id': expense.journal_id.id,
                        'period_id': period.id})
            # Journal Name
            entry['name'] = expense.name
            move = account_move_obj.create({
                'ref': entry['name'],
                'period_id': period.id,
                'journal_id': expense.journal_id.id,
                'date': expense.date
            })

            # Credit Revenue
            vals = {
                'section_id': expense.internal_section_id.id,
                'activity_id': expense.activity_id.id,
                'activity_group_id': expense.activity_group_id.id,
                'name': expense.name,
            }
            line = self.env['hr.expense.line'].create(vals)
            line.update_related_dimension(vals)
            # The Internal Charge journal must consume budget
            if not expense.journal_id.analytic_journal_id:
                raise UserError(
                    _("You have to define an analytic journal on "
                      "the '%s' journal!") %
                    (expense.journal_id.name, ))
            analytic_account = Analytic.create_matched_analytic(line)
            if not expense.activity_id.account_id:
                raise UserError(
                    _("You have to define an account code on "
                      "the '%s' activity!") %
                    (line.activity_id.name, ))
            move_line_val = {
                'move_id': move.id,
                'journal_id': expense.journal_id.id,
                'period_id': period.id,
                'analytic_account_id': analytic_account.id,
                'name': line.name,
                'quantity': 1.0,
                'debit': 0.0,
                'credit': expense.amount,
                'account_id': expense.activity_id.account_id.id,
                'partner_id': False,
                'date': expense.date,
                'date_maturity': expense.date
            }
            account_move_line_obj.with_context(ctx).create(move_line_val)

            # Debit Expense Lines
            for line in expense.line_ids:
                analytic_account = Analytic.create_matched_analytic(line)
                if not line.activity_id.account_id:
                    raise UserError(
                        _("You have to define an account code on "
                          "the '%s' activity!") %
                        (line.activity_id.name, ))
                move_line_val = {
                    'move_id': move.id,
                    'journal_id': expense.journal_id.id,
                    'period_id': period.id,
                    'analytic_account_id': analytic_account.id,
                    'name': line.name,
                    'quantity': line.unit_quantity,
                    'debit': line.total_amount,
                    'credit': 0.0,
                    'account_id': line.activity_id.account_id.id,
                    'partner_id': False,
                    'date': expense.date,
                    'date_maturity': expense.date
                }
                account_move_line_obj.with_context(ctx).create(move_line_val)
            expense.write({'account_move_id': move.id})
