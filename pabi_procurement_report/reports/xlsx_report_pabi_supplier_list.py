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
    org_name = fields.Char(
        string='Org',
    )
    categ_name = fields.Char(
        string='Supplier',
    )
    tag_name = fields.Char(
        string='Partner',
    )


    @api.onchange('org_ids')
    def onchange_orgs(self):
        res = ''
        for prg in self.org_ids:
            if res != '':
                res += ', '
            res += prg.operating_unit_id.code
        self.org_name = res

    @api.onchange('categ_ids')
    def onchange_categs(self):
        res = ''
        for categ in self.categ_ids:
            if res != '':
                res += ', '
            res += categ.name
        self.categ_name = res

    @api.onchange('tag_ids')
    def onchange_tags(self):
        res = ''
        for tag in self.tag_ids:
            if res != '':
                res += ', '
            res += tag.name
        self.tag_name = res

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
        temp_Result = None
        dom = []
        if self.categ_ids:
            dom += [('category_id', 'in', self.categ_ids._ids)]
            if not self.tag_ids:
               self.results =  Result.search(dom)
        if self.tag_ids:
            for tag in self.tag_ids: 
                temp_dom = list(dom)
                temp_dom += [('tag_ids', 'like', tag.id)] #tag_ids is fields Char
                if temp_Result == None:
                    temp_Result = Result.search(temp_dom)
                else:
                    temp_Result =  temp_Result + (Result.search(temp_dom) - temp_Result) #Remove Value Result Duplicate and Sum Result
            self.results = temp_Result
        if (not self.categ_ids) and (not self.tag_ids):
            self.results =  Result.search(dom)
            
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
    tag_ids = fields.Char(
        string='Tag ID',
        readonly=True,
    )
    tag_name = fields.Char(
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
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    account_number = fields.Integer(
        string='Account Number',
        readonly=True,
    )
    bank_name = fields.Char(
        string='Bank Name',
        readonly=True,
    )
    account_owner_name = fields.Char(
        string='Account Owner Name',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by rp.id) as id,
        rpc.id as category_id,
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
        array_to_string(array(select rt.id from res_partner_tag rt 
        LEFT JOIN res_partner_res_partner_tag_rel tag
        ON tag.res_partner_tag_id = rt.id
        where tag.res_partner_id = rp.id),',',null) as tag_ids,
        array_to_string(array(select rt.name from res_partner_tag rt 
        LEFT JOIN res_partner_res_partner_tag_rel tag
        ON tag.res_partner_tag_id = rt.id
        where tag.res_partner_id = rp.id),',',null) as tag_name,
        CONCAT(
        COALESCE(rp.phone||' ',''),
        COALESCE(rp.mobile,'')
        ) as phone,
        rp.id as partner_id,
        rp.email as email,
        rpb.acc_number as account_number,
        rpb.bank_name as bank_name,
        rpb.owner_name as account_owner_name
        FROM res_partner rp
        LEFT JOIN res_partner_res_partner_tag_rel rprptl
        ON rprptl.res_partner_id = rp.id
        LEFT JOIN res_partner_tag rpt
        ON rprptl.res_partner_tag_id = rpt.id
        LEFT JOIN res_partner_category rpc
        ON rp.category_id = rpc.id
        LEFT JOIN res_partner_bank rpb
        ON rp.id = rpb.partner_id 
        WHERE rp.supplier = True
        AND rp.employee = False
        AND rpb.active = True 
        AND rpb.default = True
        GROUP BY 
        rp.id,
        rpc.id,
        rpb.acc_number,
        rpb.bank_name,
        rpb.owner_name
        )""" % (self._table, ))