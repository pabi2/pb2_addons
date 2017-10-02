# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        res = super(AccountMove, self).post()
        for move in self:
            if move.state == 'posted':
                # move.line_id._validate_account_user_type_vs_org()
                move.line_id._validate_require_budget_vs_org()
        return res
    # @api.one
    # @api.constrains('state')
    # def _check_move_line(self):


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # @api.multi
    # def _validate_account_user_type_vs_org(self):
    #     """
    #     * Profit & Loss must have org_id
    #     * Balance Sheet must not have org_id
    #     """
    #     error1 = _('%s is Balance Sheet\nOrg is NOT required!')
    #     error2 = _('%s is Profit & Loss\nOrg is required!')
    #     for move_line in self:
    #         err_msg = False
    #         report_type = move_line.account_id.user_type.report_type
    #         # 1) Balance Sheet but have Org
    #         if report_type in ('asset', 'liability') and move_line.org_id:
    #             err_msg = error1 % (move_line.account_id.name_get()[0][1],)
    #         # 2) Profit & Loss but no Org
    #         if report_type not in ('asset', 'liability') and \
    #                 not move_line.org_id:
    #             err_msg = error2 % (move_line.account_id.name_get()[0][1],)
    #         if err_msg:
    #             raise ValidationError(err_msg)

    @api.multi
    def _validate_require_budget_vs_org(self):
        """
        * Require budget must have org id
        """
        Budget = self.env['account.budget']
        for move_line in self:
            required = Budget.trx_budget_required(move_line)
            if not required and move_line.org_id:
                raise ValidationError(
                    _('Without product or activity,\nOrg is NOT required!'))
            # 2) Profit & Loss but no Org
            if required and not move_line.org_id:
                raise ValidationError(
                    _('With product or activity,\nOrg is required!'))
