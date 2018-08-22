# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiHiringSummmary(models.TransientModel):
    _name = 'xlsx.report.pabi.hiring.summary'
    _inherit = 'xlsx.report'

    # Search Criteria
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.hiring.summary.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.hiring.summary.results']
        dom = []
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiHiringSummaryResults(models.Model):
    _name = 'xlsx.report.pabi.hiring.summary.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='OU',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    po_name = fields.Char(
        string='PO Name',
        readonly=True,
    )
    pol_name = fields.Char(
        string='POL Name',
        readonly=True,
    )
    costcenter_name = fields.Char(
        string='Center Name',
        readonly=True,
    )
    method_name = fields.Char(
        string='Method Name',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Amount Total',
        readonly=True,
    )
    currency = fields.Char(
        string='Currency',
        readonly=True,
    )
    po_date = fields.Date(
        string='PO Date',
        readonly=True,
    )
    pd_date = fields.Date(
        string='PD Date',
        readonly=True,
    )
    date_contract_start = fields.Date(
        string='Contract Start Date',
        readonly=True,
    )
    date_contract_end = fields.Date(
        string='Contract End Date',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by po.id) as id,
        po.name as po_name,
        po.amount_total,
        cur.name as currency,
        po.date_order as po_date,
        ou.id as operating_unit_id,
        (Case when ou.name = 'สำนักงานกลาง'
        then
        'สำนักงานพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ'
        else
        ou.name
	    end) as ou_name,
        rp.id as partner_id,
        (
        SELECT prl.name
        FROM purchase_request_line prl
        WHERE id = prpol.purchase_request_line_id
        LIMIT 1
        ) as prl_name,
        wa.date_contract_start as date_contract_start,
        wa.date_contract_end as date_contract_end,
        org.id as org_id
        FROM purchase_order_line pol
        LEFT JOIN purchase_order po on po.id = pol.order_id
        LEFT JOIN purchase_request_purchase_order_line_rel prpol on prpol.purchase_order_line_id = pol.id
        LEFT JOIN res_partner rp on rp.id = po.partner_id
        LEFT JOIN product_template pt on pt.id = pol.product_id
        LEFT JOIN product_category categ ON categ.id = pt.categ_id
        LEFT JOIN purchase_work_acceptance wa ON wa.order_id = po.id
        LEFT JOIN operating_unit ou on ou.id = po.operating_unit_id
        LEFT JOIN res_org org on org.operating_unit_id = ou.id
        LEFT JOIN res_currency cur on cur.id = po.currency_id
        WHERE rp.supplier = True
        AND rp.employee = False
        AND wa.state = 'done'
        AND po.state not in ('cancel' ,'draft')
	    AND categ.name like '%%จ้างเหมา%%'
        )""" % (self._table, ))