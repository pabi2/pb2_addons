# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountUnreconciledFilter(models.Model):
    _name = 'account.unreconciled.filter'
    _description = 'Filter unreconcled move line to process reconciliation'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '!=', 'view')],
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        default=lambda self: self.env['account.fiscalyear'].find(),
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        default=lambda self: self.env['account.period'].find(),
    )
    unreconciled_count = fields.Integer(
        string='Unreconciled Move Lines',
        compute='_compute_unreconciled_count',
    )

    @api.multi
    def _get_search_domain(self):
        self.ensure_one()
        domain = [('reconcile_id', '=', False),
                  ('state', '=', 'valid'),
                  ('account_id.reconcile', '=', True), ]
        if self.account_id:
            domain += [('account_id', '=', self.account_id.id)]
        if self.fiscalyear_id:
            domain += \
                [('period_id.fiscalyear_id', '=', self.fiscalyear_id.id)]
        if self.period_id:
            domain += [('period_id', '=', self.period_id.id)]
        return domain

    @api.multi
    @api.depends('fiscalyear_id', 'period_id', 'account_id')
    def _compute_unreconciled_count(self):
        MoveLine = self.env['account.move.line']
        for rec in self:
            domain = rec._get_search_domain()
            rec.unreconciled_count = MoveLine.search_count(domain)
        return True

    @api.multi
    def open_unreconciled(self):
        """ Open the view of move line with the unreconciled move lines"""
        self.ensure_one()
        MoveLine = self.env['account.move.line']
        domain = self._get_search_domain()
        lines = MoveLine.search(domain)
        name = _('Unreconciled Items')
        return self._open_move_line_list(lines.ids or [], name)

    @api.model
    def _open_move_line_list(self, move_line_ids, name):
        return {
            'name': name,
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': unicode([('id', 'in', move_line_ids)]),
        }
