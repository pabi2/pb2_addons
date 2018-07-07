# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class PayableBalanceView(models.Model):
    _name = 'payable.balance.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True,
    )
    reconcile_id = fields.Many2one(
        'account.move.reconcile',
        string='Reconcile',
        readonly=True,
    )
    doctype = fields.Selection(
        [('in_invoice', 'Supplier Invoice'),
         ('in_refund', 'Supplier Refund'),
         ('adjustment', 'Adjustment')],
        string='Doctype',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    account_code = fields.Char(
        string='Account Code',
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT aml.*, aa.code AS account_code,
                   rp.search_key AS partner_code
            FROM account_move_line aml
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN res_partner rp ON aml.partner_id = rp.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportPayableBalance(models.TransientModel):
    _name = 'xlsx.report.payable.balance'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    results = fields.Many2many(
        'payable.balance.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['payable.balance.view']
        dom = [('account_id.type', '=', 'payable'),
               ('move_id.state', '=', 'posted'),
               ('reconcile_id', '=', False),
               ('doctype', 'in', ['in_invoice', 'in_refund', 'adjustment'])]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('move_id.date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('move_id.date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('move_id.date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('move_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom, order="account_code,partner_code")
