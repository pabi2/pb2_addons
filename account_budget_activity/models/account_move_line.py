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
        """ For balance sheet item, do not create analytic line """
        # Before create, always remove analytic line if exists
        for move_line in self:
            move_line.analytic_lines.unlink()
        move_lines = self.filtered(lambda l:
                                   l.account_id.user_type.report_type
                                   not in ('asset', 'liability'))
        return super(AccountMoveLine, move_lines).create_analytic_lines()
