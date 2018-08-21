# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiPurchaseAnnual(models.TransientModel):
    _name = 'xlsx.report.pabi.purchase.annual'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.purchase.annual.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.purchase.annual.results']
        dom = []
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiPurchaseAnnualResults(models.Model):
    _name = 'xlsx.report.pabi.purchase.annual.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='OU',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    ou_name = fields.Char(
        string='OU Name',
        readonly=True,
    )
    method = fields.Char(
        string='Method',
        readonly=True,
    )
    po_count = fields.Integer(
        string='PO Count',
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

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by ou.id) as id,
        ou.id as operating_unit_id,
        org.id as org_id,
        ou.name as ou_name,
        met.name as method,
        COUNT(po.id) as po_count,
        SUM(po.amount_total) as amount_total,
        cur.name as currency
        FROM purchase_order_line pol
        LEFT JOIN purchase_order po on po.id = pol.order_id
        LEFT JOIN purchase_requisition_line reql on pol.requisition_line_id = reql.id
        LEFT JOIN purchase_requisition req on reql.requisition_id = req.id
        LEFT JOIN purchase_method met on req.purchase_method_id = met.id 
        LEFT JOIN operating_unit ou on ou.id = po.operating_unit_id
        LEFT JOIN res_org org on org.operating_unit_id = ou.id
        LEFT JOIN res_currency cur on cur.id = po.currency_id
        WHERE po.state not in ('cancel' ,'draft')
        GROUP BY ou.id,org.id,ou.name,met.name,cur.name
        ORDER BY ou.name
        )""" % (self._table, ))