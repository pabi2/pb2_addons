# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiSupplierList(models.TransientModel):
    _name = 'xlsx.report.pabi.supplier.list'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    categ_ids = fields.Many2many(
        'res.partner.category',
        string='Supplier Type',
    )
    tag_ids = fields.Many2many(
        'res.partner.tag',
        string='Supplier Tag',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.supplier.list.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.supplier.list.results']
        dom = []
        if self.tag_ids:
            dom += [('tag_id', 'in', self.tag_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiSupplierListResults(models.Model):
    _name = 'xlsx.report.pabi.supplier.list.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    category_id = fields.Many2one(
        'res.partner.category',
        string='Category',
    )
    category_name = fields.Char(
        string='Category Name',
        readonly=True,
    )
    search_key = fields.Char(
        string='Search Key',
        readonly=True,
    )
    supplier_name = fields.Char(
        string='Name',
        readonly=True,
    )
    address = fields.Text(
        string='Address',
        readonly=True,
    )
    vat = fields.Char(
        string='Tax ID',
        readonly=True,
    )
    taxbranch = fields.Char(
        string='Branch ID',
        readonly=True,
    )
    tag_id = fields.Many2one(
        'res.partner.tag',
        string='Tag ID',
    )
    tag_name = fields.Float(
        string='Tag Name',
        readonly=True,
    )
    phone = fields.Char(
        string='Phone',
        readonly=True,
    )
    email = fields.Char(
        string='Email',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by rp.id) as id,
        rp.id as category_id,
        rpc.name as category_name,
        rp.name as supplier_name,
        rp.search_key as search_key,
        CONCAT(
        COALESCE(rp.street||' ',''),
        COALESCE(rp.street2||' ',''),
        COALESCE((SELECT rct.name
            FROM res_country_township rct
            WHERE rct.id = rp.township_id)||' ',''),
        COALESCE((SELECT rcd.name
            FROM res_country_district rcd
            WHERE rcd.id = rp.district_id)||' ',''),
        COALESCE((SELECT rcp.name
            FROM res_country_province rcp
            WHERE rcp.id = rp.province_id)||' ',''),
        COALESCE(rp.zip,'')
        ) as address,
        rp.vat as vat,
        rp.taxbranch as taxbranch,
        rpt.id as tag_id,
        rpt.name as tag_name,
        CONCAT(
        COALESCE(rp.phone||' ',''),
        COALESCE(rp.mobile,'')
        ) as phone,
        rp.email as email
        FROM res_partner rp
        LEFT JOIN res_partner_res_partner_tag_rel rprptl
        ON rprptl.res_partner_id = rp.id
        LEFT JOIN res_partner_tag rpt
        ON rprptl.res_partner_tag_id = rpt.id
        LEFT JOIN res_partner_category rpc
        ON rp.category_id = rpc.id
        WHERE rp.supplier = True
        AND rp.employee = False
        )""" % (self._table, ))