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
    def _is_create_invoice(self):
        if self.pay_to == 'internal':  # Do not create invoice for IC
            return False
        return True

    @api.model
    def _is_valid_for_invoice(self):
        res = super(HRExpense, self)._is_valid_for_invoice()
        if self.pay_to == 'internal':  # Do not create invoice for IC
            raise ValidationError(
                _('For internal charge, it is not allowed to create invoice'))
        return res

    @api.multi
    def create_internal_charge_move(self):
        for expense in self:  # If IC
            if expense.pay_to != 'internal':
                raise ValidationError(
                    _('For internal charge only!'))

            Move = self.env['account.move']
            employee = expense.employee_id
            if not employee.address_home_id:
                raise UserError(_('The employee must have a home address.'))
            if not employee.address_home_id.property_account_payable.id:
                raise UserError(_('The employee must have a payable account '
                                  'set on his home address.'))
            company_currency = expense.company_id.currency_id.id
            diff_curr_p = expense.currency_id.id != company_currency
            # create the move that will contain the accounting entries
            move = Move.create(self.account_move_get(expense.id))
            # one account.move.line per expense line (+taxes..)
            eml = self.move_line_get(expense.id)
            # create one more move line,
            # a counterline for the total on payable account
            total, total_currency, eml = \
                self.compute_expense_totals(expense,
                                            company_currency,
                                            expense.name, eml)
            acc = employee.address_home_id.property_account_payable.id
            eml.append({
                'type': 'dest',
                'name': '/',
                'price': total,
                'account_id': acc,
                'date_maturity': expense.date_confirm,
                'amount_currency': diff_curr_p and total_currency or False,
                'currency_id': diff_curr_p and expense.currency_id.id or False,
                'ref': expense.name
            })
            # convert eml into an osv-valid format
            lines = map(lambda x:
                        (0, 0,
                         self.line_get_convert(x, employee.address_home_id,
                                               expense.date_confirm)), eml)
            journal = move.journal

            if journal.entry_posted:
                move.button_validate()
            move.write({'line_id': lines})
            expense.account_move_id = move
        return True
