# -*- coding: utf-8 -*-
from openerp import models, api, _
from lxml import etree
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
            move_lines = insts.mapped('move_line_id')
            line_cr_ids = filter(lambda l: isinstance(l, dict) and
                                 l.get('move_line_id') in move_lines.ids,
                                 line_cr_ids)
            line_dr_ids = filter(lambda l: isinstance(l, dict) and
                                 l.get('move_line_id') in move_lines.ids,
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
                line1 = {'account_id': defer_income_account.id,
                         'amount': -income, 'note': loan_number}
                line2 = {'activity_group_id': activity_group.id,
                         'activity_id': activity.id,
                         'account_id': income_account.id,
                         'amount': income, 'note': loan_number}
                costcenter = self._get_default_costcenter(loans)
                line1.update(costcenter)
                line2.update(costcenter)
                res['value']['multiple_reconcile_ids'] = [line1, line2]
                # Add write off OU
                if not self.env.user.default_operating_unit_id.id:
                    raise ValidationError(
                        _('User %s is not in any OU!') % self.env.user.name)
                res['value']['writeoff_operating_unit_id'] = \
                    self.env.user.default_operating_unit_id.id
        return res

    @api.model
    def _get_default_costcenter(self, loans):
        """ Get default costcenter from DV """
        costcenter = {}
        receivable_ids = loans.mapped('receivable_ids').ids
        if receivable_ids:
            self._cr.execute("""
                select distinct section_id, project_id,
                    invest_asset_id, invest_construction_phase_id
                from account_move_line
                where move_id in (
                    select move_id from account_move_line
                    where id in %s)
                and not (
                    section_id is null and project_id is null and
                    invest_asset_id is null and
                    invest_construction_phase_id is null)
            """, (tuple(receivable_ids), ))
            result = self._cr.dictfetchall()
            if len(result) == 1:
                costcenter.update(result[0])
        return costcenter

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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('set_voucher_no_create', False):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        return res


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
