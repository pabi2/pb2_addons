# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class AccountAnalyticLineView(models.Model):
    _name = 'account.analytic.line.view'
    _inherit = 'account.analytic.line'
    _auto = False

    document_id = fields.Reference(
        string='Document Number',
    )
    docline_seq = fields.Integer(
        string='Item',
    )
    date = fields.Date(
        string='Posting Date',
    )
    ref = fields.Char(
        string='Reference Doc',
    )
    contract_id = fields.Many2one(
        'purchase.contract',
        related='purchase_id.contract_id',
        string='PO Contract',
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

    def _get_sql_view(self):
        sql_view = """
            SELECT * FROM account_analytic_line
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
