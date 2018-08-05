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
        domain="[('fiscalyear_id', '=', fiscalyear_id)]",
    )
    unreconciled_count = fields.Integer(
        string='Unreconciled Move Lines',
        compute='_compute_unreconciled_count',
    )
    # Defaults
    journal_id = fields.Many2one(
        'account.journal',
        string='Write-Off Journal',
        help="When user click to open reconcile items, this value will be "
        "set as user default, to be used in Reconcile Writeoff Wizard"
    )
    writeoff_acc_id = fields.Many2one(
        'account.account',
        string='Write-Off Account',
        help="When user click to open reconcile items, this value will be "
        "set as user default, to be used in Reconcile Writeoff Wizard"
    )

    @api.onchange('fiscalyear_id')
    def _onchange_fiscalyear_id(self):
        self.period_id = False

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

    @api.model
    def _set_default_values(self, model, default_fields):
        defaults = self.env['ir.values'].search([
            ('key', '=', 'default'),
            ('model', '=', model),
            ('user_id', '=', self._uid), ])
        defaults.unlink()
        for field in default_fields:
            value = self[field] and self[field].id or False
            if value:
                self.env['ir.values'].create({
                    'key': 'default',
                    'key2': False,
                    'user_id': self._uid,
                    'company_id': self.env.user.company_id.id,
                    'name': field,
                    'value_unpickle': value,
                    'model': model,
                })
        return True

    @api.multi
    def open_unreconciled(self):
        """ Open the view of move line with the unreconciled move lines"""
        self.ensure_one()
        # Set default values to be used later in the process
        self._set_default_values('account.move.line.reconcile.writeoff',
                                 ['journal_id',
                                  'writeoff_acc_id'])
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
