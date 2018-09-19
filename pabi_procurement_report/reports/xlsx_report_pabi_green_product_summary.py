# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiGreenProductSummmary(models.TransientModel):
    _name = 'xlsx.report.pabi.green.product.summary'
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
    category_ids = fields.Many2many(
        'res.partner.category',
        'green_category_rel',
        'wizard_id',
        'category_id',
        string='Supplier Category',
    )
    sel_product = fields.Selection(
        [
            ('all', 'All'),
            ('green', 'Green'),
            ('innovation', 'Innovation'),
        ],
        string='Product',
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )
    org_name = fields.Char(
        string='Org Name',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    category_name = fields.Char(
        string='Category Name',
    )

    @api.onchange('org_ids')
    def onchange_orgs(self):
        res = ''
        for prg in self.org_ids:
            if res != '':
                res += ', '
            res += prg.operating_unit_id.code
        self.org_name = res

    @api.onchange('partner_ids')
    def onchange_partners(self):
        res = ''
        for partner in self.partner_ids:
            if res != '':
                res += ', '
            res += partner.name
        self.partner_name = res

    @api.onchange('category_ids')
    def onchange_categs(self):
        res = ''
        for categ in self.category_ids:
            if res != '':
                res += ', '
            res += categ.name
        self.category_name = res

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.green.product.summary.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.green.product.summary.results']
        dom = []
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiGreenProductSummaryResults(models.Model):
    _name = 'xlsx.report.pabi.green.product.summary.results'
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
    uom_name = fields.Char(
        string='UoM Name',
        readonly=True,
    )
    product_qty = fields.Float(
        string='Quantity',
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
    is_green_product = fields.Boolean(
        string='Green Product',
        readonly=True,
    )
    is_innovation = fields.Boolean(
        string='Innovation Product',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by po.id) as id,
        po.name as po_name,
        pt.name as pol_name,
        pol.price_unit as amount_total,
        cur.name as currency,
        po.date_order as po_date,
        ou.id as operating_unit_id,
        ou.name as ou_name,
        (SELECT value
        FROM ir_translation
        WHERE res_id = uom.id AND name LIKE 'product.uom,name') uom_name,
        rp.id as partner_id,
        pdl.is_green_product,
        org.id as org_id,
        pol.product_qty,
        pdl.is_innovation as is_innovation
        FROM purchase_order_line pol
        LEFT JOIN purchase_order po on po.id = pol.order_id
        LEFT JOIN purchase_requisition_line pdl on  pdl.id = pol.requisition_line_id
        LEFT JOIN product_uom uom on uom.id = pol.product_uom
        LEFT JOIN res_partner rp on rp.id = po.partner_id
        LEFT JOIN product_template pt on pt.id = pol.product_id
        LEFT JOIN operating_unit ou on ou.id = po.operating_unit_id
        LEFT JOIN res_org org on org.operating_unit_id = ou.id
        LEFT JOIN res_currency cur on cur.id = po.currency_id
        WHERE rp.supplier = True
        AND rp.employee = False
        AND po.state not in ('cancel' ,'draft')
        )""" % (self._table, ))