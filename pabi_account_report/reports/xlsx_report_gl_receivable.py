# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools

REFERENCE_SELECT = [('res.section', 'Section ID'),
                    ('res.project', 'Project ID'),
                    ('res.personnal.costcenter', 'Personnal Costcenter ID'),
                    ('res.invest.asset', 'Invest Asset ID'),
                    ('res.invest.construction', 'Invest Construction ID'), ]


class GLReceivableView(models.Model):
    _name = 'gl.receivable.view'
    _auto = False

    invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='Invoice Move Line',
        readonly=True,
    )
    receipt_move_line_id = fields.Many2one(
        'account.move.line',
        string='Receipt Move Line',
        readonly=True,
    )
    budget = fields.Reference(
        REFERENCE_SELECT,
        string='budget',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY
                    revenue_table.invoice_move_line_id,
                    receipt_table.receipt_move_line_id) AS id,
                    revenue_table.invoice_move_line_id AS invoice_move_line_id,
                    receipt_table.receipt_move_line_id AS receipt_move_line_id,
                CASE WHEN revenue_table.section_id IS NOT NULL THEN
                    concat('res.section,', revenue_table.section_id)
                    WHEN revenue_table.project_id IS NOT NULL THEN
                    concat('res.project,', revenue_table.project_id)
                    WHEN revenue_table.personnel_costcenter_id IS NOT NULL
                    THEN concat('res.personnel.costcenter,',
                    revenue_table.personnel_costcenter_id)
                    WHEN revenue_table.invest_asset_id IS NOT NULL THEN
                    concat('res.invest.asset,',
                    revenue_table.invest_asset_id)
                    WHEN revenue_table.invest_construction_id IS NOT NULL
                    THEN concat('res.invest.construction,',
                    revenue_table.invest_construction_id)
                ELSE NULL END AS budget
            FROM
            (SELECT aml.id AS invoice_move_line_id, aml.move_id,
                    aml.section_id, aml.project_id,
                    aml.personnel_costcenter_id, aml.invest_asset_id,
                    aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_account aa ON aml.account_id = aa.id
             LEFT JOIN account_account_type aat ON aa.user_type = aat.id
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN account_invoice ai ON aml.move_id = ai.move_id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aat.name = 'Revenue' AND am.state = 'posted'
             AND ((aml.doctype IN ('out_invoice', 'out_refund')
             AND ai.state IN ('open', 'paid', 'cancel'))
             OR aml.doctype = 'adjustment' OR iae.type = 'invoice')
             ) revenue_table
            LEFT JOIN
            (SELECT aml.move_id, aml.reconcile_id, aml.reconcile_partial_id,
                    aml.section_id, aml.project_id,
                    aml.personnel_costcenter_id, aml.invest_asset_id,
                    aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_account aa ON aml.account_id = aa.id
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aa.type = 'receivable' AND am.state = 'posted'
             OR iae.type = 'invoice'
            ) receivable_table
            ON revenue_table.move_id = receivable_table.move_id
            LEFT JOIN
            (SELECT aml.id AS receipt_move_line_id, aml.reconcile_id,
                    aml.reconcile_partial_id, aml.section_id, aml.project_id,
                    aml.personnel_costcenter_id, aml.invest_asset_id,
                    aml.invest_construction_id
             FROM account_move_line aml
             LEFT JOIN account_move am ON aml.move_id = am.id
             LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
             WHERE aml.doctype = 'receipt' AND am.state = 'posted'
             OR iae.type = 'invoice'
             ) receipt_table
             ON receivable_table.reconcile_id = receipt_table.reconcile_id
             OR receivable_table.reconcile_partial_id =
                receipt_table.reconcile_partial_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportGLReceivable(models.TransientModel):
    _name = 'xlsx.report.gl.receivable'
    _inherit = 'report.account.common'

    # Search Criteria
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
    )
    # Report Result
    results = fields.Many2many(
        'gl.receivable.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['gl.receivable.view']
        dom = []
        if self.account_ids:
            dom += [('invoice_move_line_id.account_id', 'in',
                     self.account_ids.ids)]
        if self.partner_ids:
            dom += [('invoice_move_line_id.partner_id', 'in',
                     self.partner_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('invoice_move_line_id.period_id.fiscalyear_id.date_start',
                    '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_move_line_id.period_id.fiscalyear_id.date_stop',
                    '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_move_line_id.period_id.date_start', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_move_line_id.period_id.date_stop', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_move_line_id.date_value', '>=', self.date_start)]
        if self.date_end:
            dom += [('invoice_move_line_id.date_value', '<=', self.date_end)]
        self.results = Result.search(dom)
