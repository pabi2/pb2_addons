# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiMonthlyWorkAcceptance(models.TransientModel):
    _name = 'xlsx.report.pabi.monthly.work.acceptance'
    _inherit = 'xlsx.report'

    # Search Criteria
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    date_po = fields.Date(
        string='Date Move',
    )
    date_from = fields.Date(
        string='Date From',
    )
    date_to = fields.Date(
        string='Date To',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.monthly.work.acceptance.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.monthly.work.acceptance.results']
        dom = [
            ('date_po', '>=', self.date_from),
            ('date_po', '<=', self.date_to),
        ]
        if self.operating_unit_id:
            dom += [('operating_unit_id', '=', self.operating_unit_id.id)]
        self.results = Result.search(dom)


class XLSXReportPabiMonthlyWorkAcceptanceResults(models.Model):
    _name = 'xlsx.report.pabi.monthly.work.acceptance.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    ou_code = fields.Char(
        string='OU Code',
        readonly=True,
    )
    po_name = fields.Char(
        string='PO Name',
        readonly=True,
    )
    date_po = fields.Date(
        string='PO Date',
        readonly=True,
    )
    budget_code = fields.Char(
        string='Budget Code',
        readonly=True,
    )
    budget_name = fields.Char(
        string='Budget Name',
        readonly=True,
    )
    approver = fields.Char(
        string='Approver',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Amount Total',
        readonly=True,
    )
    currency = fields.Char(
        string='Currency',
    )
    pr_text = fields.Text(
        string='PR Text',
        readonly=True,
    )
    method = fields.Char(
        string='Method',
        readonly=True,
    )
    date_doc_approve = fields.Date(
        string='PO Approved Date',
        readonly=True,
    )
    supplier_name = fields.Char(
        string='Supplier',
        readonly=True,
    )
    wa_name = fields.Char(
        string='WA Number',
        readonly=True,
    )
    date_accept = fields.Date(
        string='WA Date',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by po.id) as id,
        po.operating_unit_id,
        (SELECT value
        FROM ir_translation
        WHERE res_id = ro.id AND name LIKE 'res.org,name') ou_code,
        po.name as po_name,
        po.date_order as date_po,
        '' as budget_code,
        '' as budget_name,
        CONCAT(
        COALESCE((SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT rpt.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        LEFT JOIN res_partner_title rpt
        ON rpt.id = he.title_id
        WHERE ru.id = po.doc_approve_uid LIMIT 1) AND
            it.name LIKE 'res.partner.title,name') || ' ', ''),
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = po.doc_approve_uid) AND
            it.name LIKE 'hr.employee,first_name' LIMIT 1),
        ' ',
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = po.doc_approve_uid) AND it.name LIKE 'hr.employee,last_name' LIMIT 1) 
        ) as approver,
        CONCAT((SELECT pt.name FROM purchase_type pt
            WHERE pt.id = pd.purchase_type_id LIMIT 1),' ',pd.objective) pr_text,
        pm.name as method,
        po.amount_total,
        rc.name currency,
        CONCAT(COALESCE(rpt.name || ' ',''),rp.name) as supplier_name,
        pd.date_doc_approve,
        wa.name wa_name,
        wa.date_receive date_accept
        FROM purchase_order po
        LEFT JOIN purchase_requisition pd
        ON pd.name = po.origin
        LEFT JOIN purchase_method pm
        ON pd.purchase_method_id = pm.id
        LEFT JOIN res_partner rp
        ON po.partner_id = rp.id
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        LEFT JOIN res_currency rc
        ON rc.id = po.currency_id
        LEFT JOIN account_period ap
        ON ap.code = to_char(po.date_order,'mm/YYYY')
        LEFT JOIN res_org ro
        ON ro.id = (SELECT DISTINCT pol.org_id
        FROM purchase_order_line pol
        WHERE pol.order_id = po.id LIMIT 1)
        LEFT JOIN purchase_work_acceptance wa
        ON wa.order_id = po.id
        WHERE po.order_type LIKE 'purchase_order'
        )""" % (self._table, ))