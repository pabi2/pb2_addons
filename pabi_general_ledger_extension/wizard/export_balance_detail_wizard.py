# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ExportBalanceDetailWizard(models.TransientModel):
    _name = 'export.balance.detail.wizard'
    _inherit = 'export.xlsx.template'

    # Criteria for only account balance detail report
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        string='Target Moves',
    )
    reconcile_cond = fields.Selection(
        [('all', 'All Items'),
         ('open_item', 'Open Items'),
         ('reconciled', 'Full Reconciled')],
        string='Reconcile cond',
    )
    amount_currency = fields.Boolean(
        string='With Currency',
    )
    is_account_balance_detail_template = fields.Boolean(
        compute='_compute_is_account_balance_detail_template',
        string='Is Account Balance Detail Template ?',
    )
    move_line_ids = fields.Many2many(
        'account.move.line',
        compute='_compute_move_line',
        string='Move Line',
    )

    @api.model
    def default_get(self, fields):
        """
        Only account balance detail report
        """
        defaults = super(ExportBalanceDetailWizard, self).default_get(fields)
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model and active_id:
            general_ledger = self.env[active_model].browse(active_id)
            defaults['fiscalyear_id'] = general_ledger.fiscalyear_id.id
            defaults['account_ids'] = general_ledger.account_ids.ids
            defaults['target_move'] = general_ledger.target_move
            defaults['reconcile_cond'] = general_ledger.reconcile_cond
            defaults['amount_currency'] = general_ledger.amount_currency
        return defaults

    @api.multi
    @api.depends('template_id')
    def _compute_is_account_balance_detail_template(self):
        """
        Only account balance detail report
        """
        self.ensure_one()
        template = self.env.ref(
            'pabi_general_ledger_extension.account_balance_detail_template')
        self.is_account_balance_detail_template = False
        if self.template_id == template:
            self.is_account_balance_detail_template = True

    @api.multi
    @api.depends('is_account_balance_detail_template')
    def _compute_move_line(self):
        """
        Only account balance detail report
        """
        self.move_line_ids = False
        if self.is_account_balance_detail_template:
            TB = self.env['account.general.ledger.report']
            _x, moves = TB._get_moves(self.fiscalyear_id.id, self.target_move,
                                      self.reconcile_cond, self.account_ids,
                                      self.amount_currency)
            self.move_line_ids = TB._get_focus_moves(moves, self.period_id) \
                .sorted(key=lambda l: l.account_id.code)

    @api.multi
    def act_getfile(self):
        self.ensure_one()
        template_id = self.template_id
        res_model = self.res_model
        res_id = self.res_id
        if self.is_account_balance_detail_template:
            res_model = self._name
            res_id = self.id
        out_file, out_name = self._export_template(template_id,
                                                   res_model, res_id)
        self.write({'state': 'get', 'data': out_file, 'name': out_name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
