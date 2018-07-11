# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools

REFERENCE_SELECT = [('res.section', 'Section ID'),
                    ('res.project', 'Project ID'),
                    ('res.personnal.costcenter', 'Personnal Costcenter ID'),
                    ('res.invest.asset', 'Invest Asset ID'),
                    ('res.invest.construction', 'Invest Construction ID'), ]


class GlPayableView(models.Model):
    _name = 'gl.payable.view'
    _auto = False

    invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='Account Move Line',
        readonly=True,
    )

    payment_move_line_id = fields.Many2one(
        'account.move.line',
        string='Account Move Line',
        readonly=True,
    )

    budget = fields.Reference(
        REFERENCE_SELECT,
        string='budget',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY expense_table.invoice_move_line_id,
                payment_table.payment_move_line_id) AS id,
                expense_table.invoice_move_line_id AS invoice_move_line_id ,
                payment_table.payment_move_line_id AS payment_move_line_id,
            CASE WHEN expense_table.section_id IS NOT NULL THEN
             concat('res.section,', expense_table.section_id)
             WHEN expense_table.project_id IS NOT NULL THEN
              concat('res.project,', expense_table.project_id)
             WHEN expense_table.personnel_costcenter_id IS NOT NULL
             THEN concat('res.personnel.costcenter,',
                    expense_table.personnel_costcenter_id)
             WHEN expense_table.invest_asset_id IS NOT NULL THEN
              concat('res.invest.asset,',
              expense_table.invest_asset_id)
             WHEN expense_table.invest_construction_id IS NOT NULL
             THEN concat('res.invest.construction,',
              expense_table.invest_construction_id)
             ELSE NULL END AS budget
            FROM
            (SELECT aml.id AS invoice_move_line_id, aml.move_id, aml.section_id,aml.project_id,
             aml.personnel_costcenter_id, aml.invest_asset_id, aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_account aa ON aml.account_id = aa.id
             LEFT JOIN account_account_type aat ON aa.user_type = aat.id
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN account_invoice ai ON aml.move_id = ai.move_id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aml.doctype in ('in_invoice', 'in_refund') AND aat.name = 'Expense'
             AND am.state = 'posted' AND ai.state IN ('open', 'paid', 'cancel') OR iae.type = 'invoice') expense_table
            LEFT JOIN
            (SELECT aml.move_id, aml.reconcile_id, aml.reconcile_partial_id, aml.section_id, aml.project_id, aml.personnel_costcenter_id,
             aml.invest_asset_id, aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_account aa ON aml.account_id = aa.id
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aa.type = 'payable' AND am.state = 'posted' OR iae.type = 'invoice'
            ) payable_table ON expense_table.move_id = payable_table.move_id
            LEFT JOIN
            (SELECT aml.id AS payment_move_line_id, aml.reconcile_id, aml.reconcile_partial_id, aml.section_id, aml.project_id, aml.personnel_costcenter_id, aml.invest_asset_id, aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aml.doctype = 'payment' AND am.state = 'posted' OR iae.type = 'invoice'
             ) payment_table
             ON payable_table.reconcile_id = payment_table.reconcile_id
             OR payable_table.reconcile_partial_id = payment_table.reconcile_partial_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportGlPayable(models.TransientModel):
    _name = 'xlsx.report.gl.payable'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        'report_id', 'account_id',
        string='Accounts',
        domain=[('type', '=', 'receivable')],
    )

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )

    results = fields.Many2many(
        'gl.payable.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['gl.payable.view']
        dom = []
        if self.fiscalyear_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.date_start)]
        if self.date_end:
            dom += [('invoice_move_line_id.move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom)
