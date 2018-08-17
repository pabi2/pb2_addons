# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiStandardAsset(models.TransientModel):
    _name = 'xlsx.report.pabi.standard.asset'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
    )
    is_standard = fields.Selection(
        [
            ('all', 'All'),
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        string='Standard',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
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
        'xlsx.report.pabi.standard.asset.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.standard.asset.results']
        dom = [
            ('po_date', '>=', self.date_from),
            ('po_date', '<=', self.date_to),
        ]
        if self.is_standard:
            if self.is_standard == 'yes':
                dom += [('is_standard', '=', True)]
            elif self.is_standard == 'no':
                dom += [('is_standard', '=', False)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.method_id:
            dom += [('method_id', '=', self.method_id.id)]
        if self.partner_id:
            dom += [('partner_id', '=', self.partner_id.id)]
        if self.order_id:
            dom += [('id', '=', self.order_id.id)]
        self.results = Result.search(dom)


class XLSXReportPabiStandardAssetResults(models.Model):
    _name = 'xlsx.report.pabi.standard.asset.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    po_number = fields.Char(
        string='PO No.',
        readonly=True,
    )
    ou_name = fields.Char(
        string='OU Name',
        readonly=True,
    )
    pol_product_name = fields.Char(
        string='PO Product name',
        readonly=True,
    )
    prl_price = fields.Float(
        string='Request Line Price',
        readonly=True,
    )
    pol_price = fields.Float(
        string='PO Line Price',
        readonly=True,
    )
    supplier = fields.Char(
        string='Supplier',
        readonly=True,
    )
    brand = fields.Char(
        string='Brand',
        readonly=True,
    )
    province = fields.Char(
        string='Province',
        readonly=True,
    )
    remark = fields.Char(
        string='Remark',
        readonly=True,
    )
    warranty = fields.Char(
        string='Warranty',
        readonly=True,
    )
    is_standard = fields.Boolean(
        string='Is Standard',
        readonly=True,
    )
    po_date = fields.Date(
        string='PO Date',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Purchase Method',
    )
    price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Purchase Price Range',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )

    def init(self, cr):
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT DISTINCT
        row_number() over (order by po.id) as id,
        pp.name_template AS pol_product_name,
        po.name AS po_number,
        pol.price_unit AS pol_price,
        prql.price_unit AS prl_price,
        trim(concat(rp.title,' ',rp.name)) AS supplier,
        rcp.name AS province,
        extract(year from age(aaa.warranty_expire_date,
                              aaa.warranty_start_date))*12 +
        extract(month from age(aaa.warranty_expire_date,
                               aaa.warranty_start_date)) AS warranty,
        '' AS brand,
        aaa.name AS remark,
        prl.is_standard_asset AS is_standard,
        po.date_order AS po_date,
        po.operating_unit_id AS operating_unit_id,
        prq.purchase_method_id AS method_id,
        prq.purchase_price_range_id AS price_range_id,
        rp.id AS partner_id,
        po.id AS order_id,
        (
        SELECT id from res_org WHERE operating_unit_id = po.operating_unit_id
        ) as org_id,
        ou.name as ou_name
        FROM
        account_asset aaa
        LEFT JOIN product_product pp ON pp.id = aaa.product_id
        LEFT JOIN stock_move sm ON sm.id = aaa.move_id
        LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
        LEFT JOIN purchase_order po ON po.name = sp.origin
        LEFT JOIN res_partner rp ON rp.id = po.partner_id
        LEFT JOIN res_country_province rcp ON rcp.id = rp.province_id
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN purchase_requisition_line prl
            ON pol.requisition_line_id = prl.id
        LEFT JOIN purchase_requisition prq
            ON prl.requisition_id = prq.id
        LEFT JOIN purchase_request_purchase_requisition_line_rel prprl
            ON prl.id = purchase_requisition_line_id
        LEFT JOIN purchase_request_line prql
            ON prprl.purchase_request_line_id = prql.id
        LEFT JOIN operating_unit ou ON po.operating_unit_id = ou.id
        WHERE po.order_type = 'purchase_order'
        ORDER BY id
        )""" % (self._table, ))