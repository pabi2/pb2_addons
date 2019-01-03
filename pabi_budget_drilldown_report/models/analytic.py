# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class AccountAnalyticLineView(models.Model):
    _name = 'account.analytic.line.view'
    _inherit = 'account.analytic.line'
    _auto = False

    # This part just to ensure no write occue in this view
    purchase_request_id = fields.Many2one('purchase.request', store=False)
    purchase_id = fields.Many2one('purchase.order', store=False)
    sale_id = fields.Many2one('sale.order', store=False)
    expense_id = fields.Many2one('hr.expense.expense', store=False)
    # --
    document = fields.Char(
        string='Document Number',
    )
    # document_id = fields.Reference(
    #     string='Document Number',
    # )
    docline_sequence = fields.Integer(
        string='Item',
    )
    date_document = fields.Date(
        string='Document Date',
    )
    date = fields.Date(
        string='Posting Date',
    )
    source_document = fields.Char(
        string='Source Doc',
    )
    ref = fields.Char(
        string='Reference',
    )
    contract_id = fields.Many2one(
        'purchase.contract',
        related='purchase_id.contract_id',
        string='PO Contract',
    )
    negate_amount = fields.Float(
        string='Amount',
        help="Amount with negate sign, to show expense as positive",
    )
    budget_code = fields.Char(
        compute='_compute_budget',
        string='Budget Code',
    )
    budget_name = fields.Char(
        compute='_compute_budget',
        string='Budget Name',
    )
    name = fields.Char(
        string='Text',
    )
    activity_group_code = fields.Char(
        related='activity_group_id.code',
        string='Activity Group Code',
    )
    activity_group_name = fields.Char(
        related='activity_group_id.name',
        string='Activity Group Name',
    )
    activity_code = fields.Char(
        related='activity_id.code',
        string='Activity Code',
    )
    activity_name = fields.Char(
        related='activity_id.name',
        string='Activity Name',
    )
    activity_rpt_code = fields.Char(
        related='activity_rpt_id.code',
        string='Activity Rpt Code',
    )
    activity_rpt_name = fields.Char(
        related='activity_rpt_id.name',
        string='Activity Rpt Name',
    )
    general_account_id = fields.Many2one(
        string='Account',
    )
    account_code = fields.Char(
        related='general_account_id.code',
        string='Account Code',
    )
    account_name = fields.Char(
        related='general_account_id.name',
        string='Account Name',
    )
    docline_account_code = fields.Char(
        string='Account Code',
        compute='_compute_docline_account',
    )
    docline_account_name = fields.Char(
        string='Account Name',
        compute='_compute_docline_account',
    )
    categ_id = fields.Many2one(
        'product.category',
        related='product_id.categ_id',
        string='Product Cat Name',
    )
    product_code = fields.Char(
        related='product_id.default_code',
        string='Product Code',
    )
    product_name = fields.Char(
        related='product_id.name',
        string='Product Name',
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        related='purchase_id.requisition_id.request_ref_id.purchase_method_id',
        string='Purchase Method',
    )
    partner_code = fields.Char(
        related='partner_id.search_key',
        string='Supplier Code',
    )
    partner_name = fields.Char(
        related='partner_id.name',
        string='Supplier Name',
    )
    prepare_emp_id = fields.Many2one(
        string='Preparer',
    )
    approve_emp_id = fields.Many2one(
        string='Approver',
    )
    costcenter_code = fields.Char(
        related='costcenter_id.code',
        string='Costcenter Code',
    )
    costcenter_name = fields.Char(
        related='costcenter_id.name',
        string='Costcenter Name',
    )
    division_name = fields.Char(
        related='division_id.name',
        string='Division',
    )
    subsector_name = fields.Char(
        related='subsector_id.name',
        string='Subsector',
    )
    sector_name = fields.Char(
        related='sector_id.name',
        string='Sector',
    )
    org_name = fields.Char(
        related='org_id.name',
        string='Org',
    )
    mission_name = fields.Char(
        related='mission_id.name',
        string='Mission',
    )
    job_order_group_code = fields.Char(
        related='cost_control_id.cost_control_type_id.code',
        string='Job Order Group Code',
    )
    job_order_group_name = fields.Char(
        related='cost_control_id.cost_control_type_id.name',
        string='Job Order Group Name',
    )
    job_order_code = fields.Char(
        related='cost_control_id.code',
        string='Job Order Code',
    )
    job_order_name = fields.Char(
        related='cost_control_id.name',
        string='Job Order Name',
    )
    section_program_name = fields.Char(
        related='project_id.program_id.section_program_id.name',
        string='Section Program',
    )
    project_group_name = fields.Char(
        related='project_id.project_group_id.name',
        string='Project Group',
    )
    program_name = fields.Char(
        related='project_id.program_id.name',
        string='Program',
    )
    program_group_name = fields.Char(
        related='project_id.program_group_id.name',
        string='Program Group',
    )
    functional_area_name = fields.Char(
        related='project_id.functional_area_id.name',
        string='Functional Area',
    )
    project_manager_code = fields.Char(
        related='project_id.pm_employee_id.employee_code',
        string='Project Manager Code',
    )
    project_manager_name = fields.Char(
        compute='_compute_project_manager',
        string='Project Manager Name',
    )
    fund_name = fields.Char(
        compute='_compute_fund',
        string='Source of Fund',
    )
    fund_type = fields.Char(
        compute='_compute_fund',
        string='Fund Type',
    )
    date_start_project = fields.Date(
        related='project_id.project_date_start',
        string='Start Date',
    )
    date_end_project = fields.Date(
        related='project_id.project_date_end',
        string='End Date',
    )
    date_start_spending = fields.Date(
        related='project_id.date_start',
        string='Start Date for Spending',
    )
    date_end_spending = fields.Date(
        related='project_id.date_end',
        string="End Date for Spending",
    )
    date_start_contract = fields.Date(
        related='project_id.contract_date_start',
        string='Contract Start Date',
    )
    date_end_contract = fields.Date(
        related='project_id.contract_date_end',
        string='Contract End Date',
    )
    reason = fields.Selection(
        [('new', u'ใหม่'),
         ('replace', u'ทดแทน'),
         ('extra', u'เพิ่มเติม')],
        related='invest_asset_id.reason_purchase',
        string='Reason',
    )
    invest_construction_id = fields.Many2one(
        string='Project C',
    )
    project_c_code = fields.Char(
        related='invest_construction_id.code',
        string='Project C Code',
    )
    project_c_name = fields.Char(
        related='invest_construction_id.name',
        string='Project C Name',
    )
    date_start_project_c = fields.Date(
        related='invest_construction_id.date_start',
        string='Start Date of Project C',
    )
    date_end_project_c = fields.Date(
        related='invest_construction_id.date_end',
        string='End Date of Project C',
    )
    date_start_project_phase = fields.Date(
        related='invest_construction_phase_id.date_start',
        string='Start Date',
    )
    date_end_project_phase = fields.Date(
        related='invest_construction_phase_id.date_end',
        string='End Date',
    )
    date_start_contract_project_phase = fields.Date(
        related='invest_construction_phase_id.contract_date_start',
        string='Contract Start Date',
    )
    date_end_contract_project_phase = fields.Date(
        related='invest_construction_phase_id.contract_date_end',
        string='Contract End Date',
    )
    net_committed_amount = fields.Float(
        string='Net Commited',
    )

    @api.multi
    def _compute_docline_account(self):
        """
        For SO/PR/PO/EX, use account_id from product or activity_id
        But note that, now PR has no product yet, so it won't show anyway
        """
        for rec in self.sudo():
            account = False
            if rec.doctype in ('sale_order', 'employee_expense',
                               'purchase_request', 'purchase_order'):
                if rec.activity_id:
                    account = rec.activity_id.account_id
                if rec.product_id:
                    categ = rec.product_id.categ_id
                    if rec.doctype == 'sale_order':
                        account = categ.property_account_income_categ
                    else:
                        account = categ.property_account_expense_categ
            else:  # back to normal
                account = rec.general_account_id
            if account:
                rec.docline_account_code = account.code
                rec.docline_account_name = account.name
        return True

    @api.multi
    def _compute_budget(self):
        for rec in self:
            if rec.chartfield_id:
                rec.budget_code = rec.chartfield_id.code
                rec.budget_name = rec.chartfield_id.name

    @api.multi
    def _compute_project_manager(self):
        for rec in self:
            pm_employee = rec.project_id.pm_employee_id
            rec.project_manager_name = \
                ' '.join(list(filter(
                    lambda l: l is not False,
                    [pm_employee.title_id.name, pm_employee.first_name,
                     pm_employee.mid_name, pm_employee.last_name])))

    @api.multi
    def _compute_fund(self):
        fund_type = dict(self.env['res.fund']._columns['type'].selection)
        for rec in self:
            fund_ids = rec.project_id.fund_ids
            rec.fund_name = ', '.join(fund_ids.mapped('name'))
            rec.fund_type = \
                ', '.join([fund_type[fund.type] for fund in fund_ids])

    def _get_sql_select(self):
        sql_select = """
            aal.*, -aal.amount negate_amount,
            -- Source Document for Invoice (PO/EX) and PO (PR)
            CASE WHEN aal.doctype = 'purchase_order' THEN
                (select pr.name
                 from purchase_request_purchase_order_line_rel rel
                 join purchase_request_line prl on
                    prl.id = rel.purchase_request_line_id
                 join purchase_request pr on pr.id = prl.request_id
                 where aal.purchase_line_id = purchase_order_line_id limit 1)
            WHEN aal.doctype = 'in_invoice' THEN
                (select inv.source_document
                 from account_invoice inv
                 where replace(aal.document_id,
                               'account.invoice,', '')::int  = inv.id limit 1)
              ELSE null END as source_document,
            --
            CASE WHEN aal.doctype = 'purchase_order' AND pol.id IS NOT NULL
                    THEN pol.docline_seq
                 WHEN aal.doctype = 'sale_order' AND sol.id IS NOT NULL
                    THEN sol.docline_seq
                 WHEN aal.doctype = 'employee_expense' AND hel.id IS NOT NULL
                    THEN hel.docline_seq
                 WHEN aal.doctype = 'purchase_request' AND prl.id IS NOT NULL
                    THEN prl.docline_seq
                 ELSE NULL END AS docline_sequence,
           -- net_committed_amount for PR/PO/EX
           nullif(CASE WHEN aal.doctype = 'purchase_order'
                     AND aal.purchase_id IS NOT NULL
                   THEN (select -net_committed_amount from purchase_order po
                         where aal.purchase_id = po.id)
                WHEN aal.doctype = 'employee_expense'
                     AND aal.expense_id IS NOT NULL
                   THEN (select -net_committed_amount from hr_expense_expense x
                         where aal.expense_id = x.id)
                WHEN aal.doctype = 'purchase_request'
                     AND aal.purchase_request_id IS NOT NULL
                   THEN (select -net_committed_amount from purchase_request pr
                         where aal.purchase_request_id = pr.id)
                ELSE null END, 0) as net_committed_amount,
            --
            CASE WHEN SPLIT_PART(document_id, ',', 1) = 'hr.expense.expense'
                    THEN (SELECT create_date :: DATE
                          FROM hr_expense_expense
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 WHEN SPLIT_PART(document_id, ',', 1) = 'sale.order'
                    THEN (SELECT date_order :: DATE
                          FROM sale_order
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 WHEN SPLIT_PART(document_id, ',', 1) = 'purchase.order'
                    THEN (SELECT date_order :: DATE
                          FROM purchase_order
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 WHEN SPLIT_PART(document_id, ',', 1) = 'purchase.request'
                    THEN (SELECT create_date :: DATE
                          FROM purchase_request
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 WHEN SPLIT_PART(document_id, ',', 1) = 'account.invoice'
                    THEN (SELECT date_document :: DATE
                          FROM account_invoice
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 WHEN SPLIT_PART(document_id, ',', 1) = 'stock.picking'
                    THEN (SELECT date :: date
                          FROM stock_picking
                          WHERE id = SPLIT_PART(document_id, ',', 2) :: INT)
                 ELSE NULL END AS date_document
        """
        return sql_select

    def _get_sql_view(self):
        sql_view = """
            SELECT %s
            FROM account_analytic_line aal
            LEFT JOIN purchase_order_line pol ON aal.purchase_line_id = pol.id
            LEFT JOIN sale_order_line sol ON aal.sale_line_id = sol.id
            LEFT JOIN hr_expense_line hel ON aal.expense_line_id = hel.id
            LEFT JOIN purchase_request_line prl ON
                aal.purchase_request_line_id = prl.id
        """ % (self._get_sql_select())
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
