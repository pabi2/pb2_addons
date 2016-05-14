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
    def create(self, vals):
        """ Add dimension on move line """
        Analytic = self.env['account.analytic.account']
        analytic = False
        if vals.get('analytic_account_id', False):
            analytic = Analytic.browse(vals['analytic_account_id'])
        if analytic:
            domain = Analytic.get_analytic_search_domain(analytic)
            vals.update(dict((x[0], x[2]) for x in domain))
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, vals, check=True, update_check=True):
        res = super(AccountMoveLine, self).write(vals, check=check,
                                                 update_check=update_check)
        if vals.get('doc_id', False):
            Analytic = self.env['account.analytic.line']
            analytics = Analytic.search([('move_id', 'in', self._ids)])
            analytics.write({'doc_id': vals.get('doc_id'),
                             'doc_ref': vals.get('doc_ref')})
        return res
