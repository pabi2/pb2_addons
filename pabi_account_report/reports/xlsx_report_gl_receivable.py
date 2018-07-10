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
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    date = fields.Date(
        string='Posting Date',
        readonly=True,
    )
    name = fields.Char(
        string='Document Number',
        readonly=True,
    )
    budget = fields.Reference(
        REFERENCE_SELECT,
        string='budget',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY invoice_line.move_line_id,
                                              receipt_line.move_line_id,
                                              invoice_line.partner_id,
                                              invoice_line.date,
                                              invoice_line.name) AS id,
                   invoice_line.move_line_id AS invoice_move_line_id,
                   receipt_line.move_line_id AS receipt_move_line_id,
                   invoice_line.partner_id,
                   invoice_line.date,
                   invoice_line.name,
                   CASE WHEN invoice_line.section_id IS NOT NULL THEN
                            concat('res.section,', invoice_line.section_id)
                        WHEN invoice_line.project_id IS NOT NULL THEN
                            concat('res.project,', invoice_line.project_id)
                        WHEN invoice_line.personnel_costcenter_id IS NOT NULL
                        THEN concat('res.personnel.costcenter,',
                            invoice_line.personnel_costcenter_id)
                        WHEN invoice_line.invest_asset_id IS NOT NULL THEN
                            concat('res.invest.asset,',
                            invoice_line.invest_asset_id)
                        WHEN invoice_line.invest_construction_id IS NOT NULL
                        THEN concat('res.invest.construction,',
                            invoice_line.invest_construction_id)
                    ELSE NULL END AS budget
            FROM
            (SELECT aml.id AS move_line_id,
                   aml.reconcile_id, aml.reconcile_partial_id,
                   aml.partner_id, am.date, am.name,
                   aml.section_id, aml.project_id, aml.personnel_costcenter_id,
                   aml.invest_asset_id, aml.invest_construction_id
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN account_account_type aat ON aa.user_type = aat.id
            LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
            LEFT JOIN account_invoice ai ON aml.move_id = ai.move_id
            WHERE am.state = 'posted'
            AND aml.doctype IN ('out_invoice', 'out_refund', 'adjustment')
            AND aat.code = 'Revenue'
            AND ai.state IN ('open', 'paid')
            OR iae.type = 'invoice'
            ) invoice_line

            LEFT JOIN

            (SELECT aml.id AS move_line_id,
                   aml.reconcile_id, aml.reconcile_partial_id,
                   aml.section_id, aml.project_id, aml.personnel_costcenter_id,
                   aml.invest_asset_id, aml.invest_construction_id
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            LEFT JOIN account_account_type aat ON aa.user_type = aat.id
            LEFT JOIN interface_account_entry iae ON iae.move_id = aml.move_id
            WHERE am.state = 'posted'
            AND aml.doctype IN ('receipt')
            OR iae.type = 'payment'
            AND aat.code = 'Revenue'
            ) receipt_line
             ON invoice_line.reconcile_id = receipt_line.reconcile_id
             OR invoice_line.reconcile_partial_id =
                receipt_line.reconcile_partial_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportGLReceivable(models.TransientModel):
    _name = 'xlsx.report.gl.receivable'
    _inherit = 'report.account.common'

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
