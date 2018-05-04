# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def recompute_voucher_lines(self, partner_id, journal_id,
                                price, currency_id, ttype, date):
        res = super(AccountVoucher, self).recompute_voucher_lines(
            partner_id, journal_id,
            price, currency_id, ttype, date)
        # Only scope down to selected invoices
        if self._context.get('filter_loans', False):
            line_cr_ids = res['value']['line_cr_ids']
            line_dr_ids = res['value']['line_dr_ids']

            Plan = self.env['loan.installment.plan']
            Loan = self.env['loan.installment']
            loan_ids = self._context.get('filter_loans')
            inst_ids = self._context.get('filter_loan_installments')
            insts = False
            if inst_ids:
                insts = self.env['loan.installment.plan'].browse(inst_ids)
            else:
                insts = Plan.search([('loan_install_id', 'in', loan_ids),
                                     ('reconcile_id', '=', False)])
            move_line_ids = insts.mapped('move_line_id').ids
            line_cr_ids = filter(lambda l: isinstance(l, dict) and
                                 l.get('move_line_id') in move_line_ids,
                                 line_cr_ids)
            line_dr_ids = filter(lambda l: isinstance(l, dict) and
                                 l.get('move_line_id') in move_line_ids,
                                 line_dr_ids)
            res['value']['line_cr_ids'] = line_cr_ids
            res['value']['line_dr_ids'] = line_dr_ids
            # Additional dr/cr
            income = sum(insts.mapped('income'))
            if income > 0.0:
                company = self.env.user.company_id
                defer_income_account = company.loan_defer_income_account_id
                income_account = company.loan_income_account_id
                activity_group = company.loan_income_activity_group_id
                activity = company.loan_income_activity_id
                loans = Loan.browse(loan_ids)
                loan_number = ', '.join(loans.mapped('name'))
                res['value']['multiple_reconcile_ids'] = [
                    {'account_id': defer_income_account.id,
                     'amount': -income,
                     'note': loan_number},
                    {'activity_group_id': activity_group.id,
                     'activity_id': activity.id,
                     'account_id': income_account.id,
                     'amount': income,
                     'note': loan_number},
                ]
                # Add write off OU
                if not self.env.user.default_operating_unit_id.id:
                    raise ValidationError(
                        _('User %s is not in any OU!') % self.env.user.name)
                res['value']['writeoff_operating_unit_id'] = \
                    self.env.user.default_operating_unit_id.id
        return res

    @api.model
    def writeoff_move_line_get(self, voucher_id, line_total,
                               move_id, name,
                               company_currency, current_currency):
        """ Hack by passing force_run_writeoff """
        voucher_brw = self.browse(voucher_id)
        if voucher_brw.multiple_reconcile_ids:
            self = self.with_context(force_run_writeoff=True)
        return super(AccountVoucher, self).writeoff_move_line_get(
            voucher_id, line_total, move_id, name,
            company_currency, current_currency)


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.multi
    def _compute_invoice_taxbranch_id(self):
        super(AccountVoucherLine, self)._compute_invoice_taxbranch_id()
        for rec in self:
            if not rec.invoice_taxbranch_id:
                # Find if this move_id belongs to any loan installment.
                loan = self.env['loan.installment'].search(
                    [('move_id', '=', rec.move_line_id.move_id.id)])
                if not loan:
                    continue
                # if len(loan) > 1:
                #   raise ValidationError(_('1 move_id belongs to > 1 loan!'))
                rec.invoice_taxbranch_id = loan[0].taxbranch_id
