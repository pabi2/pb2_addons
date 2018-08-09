# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiStockCardForAccounting(models.TransientModel):
    _name = 'xlsx.report.pabi.stock.card.for.accounting'
    _inherit = 'xlsx.report'

    # Search Criteria
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    category_id = fields.Many2one(
        'product.category',
        string='Category',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    date_move = fields.Date(
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
        'xlsx.report.pabi.stock.card.for.accounting.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.stock.card.for.accounting.results']
        dom = [
            ('date_move', '>=', self.date_from),
            ('date_move', '<=', self.date_to),
        ]
        if self.operating_unit_id:
            dom += [('operating_unit_id', '=', self.operating_unit_id.id)]
        if self.product_id:
            dom += [('product_id', '=', self.product_id.id)]
        if self.category_id:
            dom += [('category_id', '=', self.category_id.id)]
        if self.location_id:
            dom += [
                '|',
                ('src_location_id', '=', self.locaiton_id.id),
                ('dest_location_id', '=', self.locaiton_id.id),
            ]
        self.results = Result.search(dom)


class XLSXReportPabiStockCardForAccountingResults(models.Model):
    _name = 'xlsx.report.pabi.stock.card.for.accounting.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    supplier = fields.Char(
        string='Supplier',
        readonly=True,
    )
    tax_id = fields.Char(
        string='Tax ID',
        readonly=True,
    )
    address = fields.Text(
        string='Address',
        readonly=True,
    )
    plant = fields.Char(
        string='Plant',
        readonly=True,
    )
    product_name = fields.Char(
        string='Product Name',
        readonly=True,
    )
    category_name = fields.Char(
        string='Category Name',
        readonly=True,
    )
    grgi_slip = fields.Char(
        string='GRGI Slip',
        readonly=True,
    )
    date_move = fields.Date(
        string='Date',
    )
    src_loc_id = fields.Many2one(
        'stock.location',
        string='Source Location ID',
    )
    src_loc_name = fields.Char(
        string='Source Location Name',
        readonly=True,
    )
    dest_loc_id = fields.Many2one(
        'stock.location',
        string='Destinatio Location ID',
    )
    dest_loc_name = fields.Char(
        string='Destination Location Name',
        readonly=True,
    )
    price_unit = fields.Float(
        string='Price Unit',
        readonly=True,
    )
    product_uom_qty = fields.Float(
        string='Quantity',
        readonly=True,
    )
    balance = fields.Float(
        string='Quantity',
        readonly=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        readonly=True,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    category_id = fields.Many2one(
        'product.category',
        string='Category',
    )

    def init(self, cr):
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT DISTINCT
        row_number() over (order by sm.id) id,
        ou.id operating_unit_id,
        pp.id product_id,
        pc.id category_id,
        rp.name supplier,
        rp.vat tax_id,
        CONCAT(
        COALESCE(rp.street||' ',''),
        COALESCE(rp.street2||' ',''),
        COALESCE((SELECT rct.name FROM res_country_township rct
            WHERE rct.id = rp.township_id)||' ',''),
        COALESCE((SELECT rcd.name FROM res_country_district rcd
            WHERE rcd.id = rp.district_id)||' ',''),
        COALESCE((SELECT rcp.name FROM res_country_province rcp
            WHERE rcp.id = rp.province_id)||' ',''),
        COALESCE(rp.zip,'')
        ) address,
        ou.name plant,
        ptmpl.name product_name,
        pc.name category_name,
        pu.name uom,
        sm.date date_move,
        pwa.name grgi_slip,
        sloc.id src_loc_id,
        dloc.id dest_loc_id,
        sloc.name src_loc_name,
        dloc.name dest_loc_name,
        sm.price_unit,
        sm.product_uom_qty,
        0.0 as balance,
        0.0 as balance_qty
        FROM stock_move sm
        LEFT JOIN stock_picking sp
        ON sp.id = sm.picking_id
        LEFT JOIN stock_location sloc
        ON sloc.id = sm.location_id
        LEFT JOIN stock_location dloc
        ON dloc.id = sm.location_dest_id
        LEFT JOIN purchase_work_acceptance pwa
        ON pwa.id = sp.acceptance_id
        LEFT JOIN operating_unit ou
        ON ou.id = sp.operating_unit_id
        LEFT JOIN res_partner rp
        ON rp.id = ou.partner_id
        LEFT JOIN product_product pp
        ON pp.id = sm.product_id
        LEFT JOIN product_template ptmpl
        ON ptmpl.id = pp.product_tmpl_id
        LEFT JOIN product_category pc
        ON pc.id = ptmpl.categ_id
        LEFT JOIN product_uom pu
        ON pu.id = ptmpl.uom_po_id
        LEFT JOIN purchase_work_acceptance_line pwal
        ON pwal.acceptance_id = sp.acceptance_id
        WHERE sm.state = 'done'
        ORDER BY id
        )""" % (self._table, ))