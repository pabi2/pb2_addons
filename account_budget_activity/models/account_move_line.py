# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )

    @api.model
    def _update_analytic_dimension(self, vals):
        """ Add dimension on move line """
        Analytic = self.env['account.analytic.account']
        analytic = False
        if vals.get('analytic_account_id', False):
            analytic = Analytic.browse(vals['analytic_account_id'])
        if analytic:
            domain = Analytic.get_analytic_search_domain(analytic)
            vals.update(dict((x[0], x[2]) for x in domain))
        return vals

    @api.model
    def create(self, vals):
        vals = self._update_analytic_dimension(vals)
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def create_analytic_lines(self):
        """ Create Analytic Line only when,
            - Is not BS and has (Activity or Product) """
        # Before create, always remove analytic line if exists
        for move_line in self:
            move_line.analytic_lines.unlink()
        move_lines = self._budget_eligible_move_lines()
        return super(AccountMoveLine, move_lines).create_analytic_lines()

    # @api.multi
    # def _budget_eligible_move_lines(self):
    #     move_lines = self.filtered(
    #         lambda l:
    #         # kittiu: It seem NSTDA asset to charge budget !!!
    #         # (l.account_id.user_type.report_type  # Not BS account
    #         #  not in ('asset', 'liability')) and
    #         (l.activity_id or l.product_id)  # Is Activity or Product
    #     )
    #     return move_lines
    @api.multi
    def _budget_eligible_move_lines(self):
        """ To be eligible, move line must,
        * With journal with analytic_journal
        * Have product or activity
        * Have AG """
        Budget = self.env['account.budget']
        move_lines = self.filtered(lambda l: Budget.trx_budget_required(l) and
                                   l.journal_id.analytic_journal_id and
                                   l.activity_group_id)
        return move_lines
