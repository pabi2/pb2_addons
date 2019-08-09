# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiMonthlyWorkAcceptance(models.TransientModel):
    _name = 'xlsx.report.pabi.monthly.work.acceptance'
    _inherit = 'xlsx.report'

    # Search Criteria
    # operating_unit_id = fields.Many2one(
    #     'operating.unit',
    #     string='Operating Unit',
    # )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Supplier',
    )
    partner_tag_ids = fields.Many2many(
        'res.partner.tag',
        string='Supplier Tag',
    )
    partner_category_ids = fields.Many2many(
        'res.partner.category',
        'monthly_report_categ_rel',
        'report_id', 'categlory_id',
        string='Supplier Type',
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
    )
    category_name = fields.Char(
        string="Category Name",
    )
    org_name = fields.Char(
        string="Org Name",
    )
    partner_name = fields.Char(
        string="Partner Name",
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.monthly.work.acceptance.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.onchange('partner_category_ids')
    def onchange_categs(self):
        res = ''
        for categ in self.partner_category_ids:
            if res != '':
                res += ', '
            res += categ.name
        self.category_name = res

    @api.onchange('partner_ids')
    def onchange_partners(self):
        res = ''
        for partner in self.partner_ids:
            if res != '':
                res += ', '
            res += partner.name
        self.partner_name = res

    @api.onchange('org_ids')
    def onchange_orgs(self):
        res = ''
        for org in self.org_ids:
            if res != '':
                res += ', '
            res += org.operating_unit_id.code
        self.org_name = res

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.monthly.work.acceptance.results']
        dom = [
            ('date_po', '>=', self.date_from),
            ('date_po', '<=', self.date_to),
        ]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiMonthlyWorkAcceptanceResults(models.Model):
    _name = 'xlsx.report.pabi.monthly.work.acceptance.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Supplier Category',
    )
    ou_name = fields.Char(
        string='OU name',
        readonly=True,
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
    product_category_name = fields.Char(
        string='Category name',
        readonly=True,
    )
    supplier_invoice = fields.Char(
        readonly=True,
    )
    date_receive = fields.Date(
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by po.id) as id,
        po.operating_unit_id,
        ou.name as ou_name,
        (
        SELECT id from res_org WHERE operating_unit_id = po.operating_unit_id
        LIMIT 1
        ) as org_id,
        (SELECT
        (Case when value = 'สำนักงานกลาง'
        then
        'สำนักงานพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ'
        else
        value
	    end)
        FROM ir_translation
        WHERE res_id = ro.id AND name LIKE 'res.org,name') ou_code,
        po.name as po_name,
        po.date_order as date_po,
        (
        select rc.code
        from purchase_order_line pol
        left join purchase_order po2 on po2.id = pol.order_id
        left join res_costcenter rc on rc.id = pol.costcenter_id  
        WHERE po2.id = po.id
        LIMIT 1
        ) as budget_code,
        (
        select rc.name_short
        from purchase_order_line pol
        left join purchase_order po2 on po2.id = pol.order_id
        left join res_costcenter rc on rc.id = pol.costcenter_id  
        WHERE po2.id = po.id
        LIMIT 1
        ) as budget_name,
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
        po.partner_id,
        pd.date_doc_approve,
        wa.name wa_name,
        wa.supplier_invoice,
        wa.date_receive,
        wa.date_receive date_accept,
        rpc.id as category_id,
        (
        select pc.name
        from purchase_order_line pol
        left join purchase_order po2 on po2.id = pol.order_id
        left join product_template pt on pt.id = pol.product_id  
        left join product_category pc on pc.id = pt.categ_id  
        WHERE po2.id = po.id
        LIMIT 1
        ) as  product_category_name
        FROM purchase_order po
        LEFT JOIN operating_unit ou
        ON ou.id = po.operating_unit_id
        LEFT JOIN purchase_requisition pd
        ON pd.name = po.origin
        LEFT JOIN purchase_method pm
        ON pd.purchase_method_id = pm.id
        LEFT JOIN res_partner rp
        ON po.partner_id = rp.id
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        LEFT JOIN res_partner_category rpc
        ON rp.category_id = rpc.id
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