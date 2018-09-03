# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiProcurementResult(models.TransientModel):
    _name = 'xlsx.report.pabi.procurement.result'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Supplier',
    )
    tag_ids = fields.Many2many(
        'res.partner.tag',
        string='Supplier Type',
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.procurement.result.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.procurement.result.results']
        dom = []
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiProcurementResultResults(models.Model):
    _name = 'xlsx.report.pabi.procurement.result.results'
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
    wa_date = fields.Date(
        string='WA Date',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by po.id) as id,
        po.name as po_name,
        pol.name as pol_name,
        COALESCE((SELECT value FROM ir_translation it
        WHERE it.res_id = rc.id AND
            it.name LIKE 'res.costcenter,name'), '') as costcenter_name,
        pm.name as method_name,
        po.amount_total,
        cur.name as currency,
        pd.ordering_date as pd_date,
        po.date_order as po_date,
        ou.id as operating_unit_id,
        rp.id as partner_id,
        wa.date_accept as wa_date,
        org.id as org_id
        FROM purchase_order_line pol
        LEFT JOIN purchase_order po on po.id = pol.order_id
        LEFT JOIN res_partner rp on rp.id = po.partner_id
        LEFT JOIN purchase_requisition pd ON pd.id = po.requisition_id
        LEFT JOIN purchase_method pm ON pm.id = pd.purchase_method_id
        LEFT JOIN purchase_work_acceptance wa ON wa.order_id = po.id
        LEFT JOIN operating_unit ou on ou.id = po.operating_unit_id
        LEFT JOIN res_org org on org.operating_unit_id = ou.id
        LEFT JOIN res_costcenter rc on rc.id = pol.costcenter_id  
        LEFT JOIN res_currency cur on cur.id = po.currency_id
        WHERE rp.supplier = True
        AND rp.employee = False
        AND wa.state = 'done'
        AND po.state not in ('cancel' ,'draft')
        )""" % (self._table, ))