# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    pay_to = fields.Selection(
        selection_add=[('internal', 'Internal Charge')],
    )
    internal_charge = fields.Boolean(
        string='IC',
        compute='_compute_internal_charge',
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

    @api.one
    @api.constrains('pay_to', 'line_ids')
    def _check_internal_charge_activity(self):
        if self.internal_charge:
            ic = list(set(self.line_ids.mapped('activity_id.internal_charge')))
            if len(ic) > 1 or \
                    (len(ic) == 1 and ic[0] != (self.internal_charge)):
                raise ValidationError(
                    _('Not all activities are internal charge!'))

    @api.multi
    @api.depends('pay_to')
    def _compute_internal_charge(self):
        for rec in self:
            rec.internal_charge = rec.pay_to == 'internal'

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
            raise ValidationError(
                _("You have to define an analytic journal on "
                  "the '%s' journal!") %
                (journal.name, ))
        vals = {
            'operating_unit_id': expense.operating_unit_id.id,
            'ref': expense.number,
            'period_id': period.id,
            'journal_id': journal.id,
            'date': expense.date
        }
        return vals

    @api.model
    def _prepare_move_line(self, move, expense, name, analytic_account_id,
                           account_id, debit=0.0, credit=0.0):
        vals = {
            'operating_unit_id': move.operating_unit_id.id,
            'move_id': move.id,
            'journal_id': move.journal_id.id,
            'period_id': move.period_id.id,
            'analytic_account_id': analytic_account_id,
            'name': name,
            'quantity': 1.0,
            'debit': debit,
            'credit': credit,
            'account_id': account_id,
            'partner_id': False,
            'date': move.date,
            'date_maturity': move.date
        }
        # Internal Charge
        if expense.pay_to == 'internal':
            vals['charge_type'] = 'internal'
        return vals

    @api.multi
    def create_internal_charge_move(self):
        AccountMove = self.env['account.move']
        Analytic = self.env['account.analytic.account']
        Expense = self.env['hr.expense.line']
        Period = self.env['account.period']
        for expense in self:
            periods = Period.find(expense.date)
            period = periods and periods[0] or False
            ctx = self._context.copy()
            ctx.update({'company_id': expense.company_id.id,
                        'period_id': period.id})
            # ============== Create 1st JE for Revenue ==============
            # Cr: Revenue
            rev_journal = expense.rev_ic_journal_id
            ctx.update({'journal_id': rev_journal.id})
            # move header
            rev_move_vals = self._prepare_move(expense, rev_journal, period)
            rev_move = AccountMove.create(rev_move_vals)
            # Credit each expense line
            rev_move_lines = []
            for line in expense.line_ids:
                # Find the reference revenue activity for this activity
                activity = line.inrev_activity_id
                activity_group = line.inrev_activity_group_id
                if not activity or not activity_group:
                    raise ValidationError(
                        _('No revenue AG/A for line %s!') % line.display_name)
                temp_exp_line_dict = {
                    'expense_id': expense.id,
                    'project_id': expense.internal_project_id.id,
                    'section_id': expense.internal_section_id.id,
                    'activity_id': activity.id,
                    'activity_group_id': activity_group.id,
                    'name': line.name,
                }
                temp_exp_line = Expense.create(temp_exp_line_dict)
                temp_exp_line.update_related_dimension(temp_exp_line_dict)
                analytic_account = \
                    Analytic.create_matched_analytic(temp_exp_line)
                temp_exp_line.unlink()  # destroy
                rev_cr_vals = self._prepare_move_line(rev_move,
                                                      expense,
                                                      line.name,
                                                      analytic_account.id,
                                                      activity.account_id.id,
                                                      debit=0.0,
                                                      credit=line.total_amount)
                rev_move_lines.append((0, 0, rev_cr_vals))
#                 AccountMoveLine.with_context(ctx).create(rev_cr_vals)
            # Dr: Internal Charge
            account_id = rev_journal.default_debit_account_id.id
            rev_dr_vals = self._prepare_move_line(rev_move,
                                                  expense,
                                                  expense.name,
                                                  False,
                                                  account_id,
                                                  debit=expense.amount,
                                                  credit=0.0)
#             AccountMoveLine.with_context(ctx).create(rev_dr_vals)
            rev_move_lines.append((0, 0, rev_dr_vals))
            rev_move.with_context(ctx).write({'line_id': rev_move_lines})
            # ============== Create 2nd JE for Expense ==============
            exp_journal = expense.exp_ic_journal_id
            ctx.update({'journal_id': exp_journal.id})
            # move header
            exp_move_vals = self._prepare_move(expense, exp_journal, period)
            exp_move = AccountMove.create(exp_move_vals)
            exp_move_lines = []
            # Debit each expense line
            for line in expense.line_ids:
                analytic_account = Analytic.create_matched_analytic(line)
                account_id = line.activity_id.account_id.id
                exp_dr_vals = self._prepare_move_line(exp_move, expense,
                                                      line.name,
                                                      analytic_account.id,
                                                      account_id,
                                                      debit=line.total_amount,
                                                      credit=0.0)
                exp_move_lines.append((0, 0, exp_dr_vals))

            # Cr: Internal Charge (equel to Dr: Internal Charge)
            exp_cr_vals = rev_dr_vals.copy()
            exp_cr_vals.update({
                'move_id': exp_move.id,
                'analytic_account_id': False,
                'debit': False,
                'credit': rev_dr_vals['debit'],
                'account_id': exp_journal.default_credit_account_id.id
            })
            # AccountMoveLine.with_context(ctx).create(exp_cr_vals)
            exp_move_lines.append((0, 0, exp_cr_vals))
            exp_move.with_context(ctx).write({'line_id': exp_move_lines})
            expense.write({'rev_ic_move_id': rev_move.id,
                           'exp_ic_move_id': exp_move.id})
            # Post and budget check_budget
            ctx = {'force_no_budget_check': True}
            rev_move.with_context(ctx).post()  # For revenue, always by pass
            if expense.pay_to == 'internal' and \
                    period.fiscalyear_id.control_ext_charge_only:
                exp_move.with_context(ctx).post()
            else:
                exp_move.post()

    @api.multi
    def write(self, vals):
        pay_to = self.mapped('pay_to')
        if 'internal' in pay_to:
            if len(pay_to) == 1:
                self = self.with_context(no_create_analytic_line=True)
            else:
                raise ValidationError(_('> 1 type of pay_to'))
        return super(HRExpense, self).write(vals)


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    inrev_activity_id = fields.Many2one(
        'account.activity',
        string='Activity (Rev)',
        domain="[('budget_method', '=', 'revenue'),"
        "('inexp_activity_ids', 'in', [activity_id])]",
    )
    inrev_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group (Rev)',
        compute='_compute_inrev_activity_group_id',
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='expense_id.employee_id',
        readonly=True,
        store=True,
    )
    employee_section_id = fields.Many2one(
        'res.section',
        string='Section',
        related='expense_id.section_id',
        readonly=True,
        store=True,
    )
    expense_name = fields.Char(
        string='Description',
        related='expense_id.name',
        readonly=True,
    )
    user_ic_allowed = fields.Boolean(
        string='Current user allowed',
        compute='_compute_user_ic_allowed',
        search='_search_user_ic_allowed',
        store=False,  # Must be virtual field
        help="- For Secion IC, all user in same section is allowed to accept."
        "\n- For Project IC, only project manager is allowed to accept.",
    )

    @api.model
    def _search_user_ic_allowed(self, operator, value):
        # Find expense with same same internal_section_id as login user
        # or login user is PM of the internal_project_id
        internal_charge = ('expense_id.pay_to', '=', 'internal')
        section_domain = ('expense_id.internal_section_id', '=',
                          self.env.user.employee_id.section_id.id)
        project_domain = ('expense_id.internal_project_id.pm_employee_id', '=',
                          self.env.user.employee_id.id)
        domain = [internal_charge, '|', section_domain, project_domain]
        return [('id', 'in', self.search(domain).ids)]

    @api.multi
    def _compute_user_ic_allowed(self):
        for line in self:
            expense = line.expense_id
            user_ic_allowed = False
            if expense.pay_to == 'internal':
                if expense.internal_section_id:
                    # Only user in the same Section
                    if self.env.user.employee_id.section_id == \
                            expense.internal_section_id:
                        user_ic_allowed = True
                elif expense.internal_project_id:
                    # Only PM
                    if self.env.user.employee_id == \
                            expense.internal_project_id.pm_employee_id:
                        user_ic_allowed = True
            line.user_ic_allowed = user_ic_allowed

    @api.multi
    @api.depends('inrev_activity_id')
    def _compute_inrev_activity_group_id(self):
        for rec in self:
            if not rec.inrev_activity_id:
                continue
            activity_groups = rec.inrev_activity_id.activity_group_ids
            if len(activity_groups) != 1:
                raise ValidationError(
                    _('Invalid group setup for revenue activity %s.\n'
                      'Revenue activity must belong to one activity group') %
                    (rec.inrev_activity_id.name))
            rec.inrev_activity_group_id = activity_groups[0]

    @api.model
    def _get_inrev_activity(self, activity_id):
        """ Only if 1-1, assign invrev_activity, else False """
        inrev_activity = False
        activity = self.env['account.activity'].browse(activity_id)
        if activity and activity.internal_charge:
            inrev_activities = activity.inrev_activity_ids
            if len(inrev_activities) == 1:
                inrev_activity = inrev_activities[0]
        return inrev_activity and inrev_activity.id or False

    @api.model
    def create(self, vals):
        if vals.get('activity_id', False) and \
                not vals.get('inrev_activity_id', False):
            inrev_activity_id = self._get_inrev_activity(vals['activity_id'])
            vals.update({'inrev_activity_id': inrev_activity_id})
        return super(HRExpenseLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('activity_id', False) and \
                not vals.get('inrev_activity_id', False):
            inrev_activity_id = self._get_inrev_activity(vals['activity_id'])
            vals.update({'inrev_activity_id': inrev_activity_id})
        return super(HRExpenseLine, self).write(vals)
