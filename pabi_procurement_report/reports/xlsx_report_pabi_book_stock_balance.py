# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiBookStockBalance(models.TransientModel):
    _name = 'xlsx.report.pabi.book.stock.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Location',
        default=lambda self: self.env['stock.location'].\
        search([('id','in',(246,247,249,252,256,257,258))])
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Product',
    )
    ou_name = fields.Char(
        string='OU Name',
    )
    location_name = fields.Char(
        string='Loc Name',
    )
    category_ids = fields.Many2many(
        'product.category',
        string='Category',
        default=lambda self: self.env['product.category'].\
        search([('id','in',(2005,2006))])
    )
    active = fields.Selection(
        [('True', 'True'),
         ('False', 'False')],
        string="Active",
        default='True')
    # date_to = fields.Date(
    #     string='To Date',
    #     required=True,
    # )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.book.stock.balance.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.onchange('org_ids')
    def onchange_orgs(self):
        res = ''
        for prg in self.org_ids:
            if res != '':
                res += ', '
            res += prg.operating_unit_id.code
        self.ou_name = res

    @api.onchange('location_ids')
    def onchange_loc(self):
        res = ''
        for loc in self.location_ids:
            if res != '':
                res += ', '
            res += loc.name
        self.location_name = res

    """@api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.stock.balance.results']
        dom = [
            '|',
            ('loc_id', 'in', self.location_ids.ids),
            ('loc_dest_id', 'in', self.location_ids.ids),
        ]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.product_ids:
            dom += [('product_id', '=', self.product_ids._ids)]
        # if self.date_to:
        #     dom = [
        #         ('date_transfer', '>=', self.date_start),
        #         ('date_transfer', '<=', self.date_end),
        #     ]
        self.results = Result.search(dom)"""
        
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.book.stock.balance.results']
        dom = []
        if self.location_ids:
            dom += [('loc_id', 'in', self.location_ids.ids)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids.ids)]
        if self.product_ids:
            dom += [('product_id', 'in', self.product_ids.ids)]
        if self.category_ids:
            dom += [
                '|',
                ('category_id', 'in', self.category_ids._ids),
                ('parent_id', 'in', self.category_ids._ids)
            ]
        if self.active:
            if self.active == 'True':
                active = True
            else:
                active = False
            dom += [('product_active','=',active)]
        self.results = Result.search(dom)
    


class XLSXReportPabiStockBalanceResults(models.Model):
    _name = 'xlsx.report.pabi.book.stock.balance.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    product_code = fields.Char(
        string='Product Code',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    product_name = fields.Char(
        string='Product Name',
        readonly=True,
    )
    price = fields.Float(
        string='Price',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    ou_name = fields.Char(
        string='OU Name',
        readonly=True,
    )
    loc_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    #loc_dest_id = fields.Many2one(
    #    'stock.location',
    #    string='Location',
    #)
    location_name = fields.Char(
        string='Location Name',
        readonly=True,
    )
    uom = fields.Char(
        string='UoM',
        readonly=True,
    )
    currency = fields.Char(
        string='Currency',
        readonly=True,
    )
    category_id = fields.Many2one(
        'product.category',
        string='Category',
    )
    category_name = fields.Char(
        string='Category Name',
        readonly=True,
    )
    parent_id = fields.Many2one(
        'product.category',
        string='Parent Category',
    )
    product_active = fields.Boolean(
        string='Product Active',
        readonly=True,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template ID',
        readonly=True,
    )

    standard_price = fields.Float(
        string='Standard Price',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT q.id as stock_id,row_number() over (order by p.ean13) as id,
            t.name as product_name,
            q.product_id as product_id,
            p.default_code as product_code,
            q.location_id as loc_id,
            sl.name as location_name, 
            q.qty as balance,
            COALESCE((
            select CAST(value_float as decimal(1000,4)) from ir_property where res_id = concat('product.template,',t.id) 
                and type='float' order by create_date,write_date desc limit 1 ),0.0) as standard_price,
            COALESCE(
            CAST((select CAST(value_float as decimal(1000,4)) from ir_property where res_id = concat('product.template,',t.id) 
                and type='float' order by create_date,write_date desc limit 1 ) * q.qty as decimal(1000,2)),0.0) as price,
            puom.name as uom,
            ou.name as ou_name,
            rc.name as currency,
            (SELECT id from res_org WHERE operating_unit_id = ou.id) as org_id,
            pc.id category_id,
            pc.name as category_name,
            pc.parent_id parent_id,
            p.active as product_active,
            t.id as product_tmpl_id
            FROM public.stock_quant q
            left join stock_location sl on q.location_id = sl.id
            left join operating_unit ou on sl.operating_unit_id = ou.id 
            left join product_product p on q.product_id = p.id 
            left join product_template t on p.product_tmpl_id = t.id
            left join product_uom puom on t.uom_id = puom.id
            left join res_company com on com.id = t.company_id
            left join res_currency rc on com.currency_id = rc.id
            left join product_category pc on pc.id = t.categ_id
            group by t.id, sl.name, q.product_id, puom.name, ou.id, ou.name, rc.name, p.default_code, q.location_id,pc.id,pc.name,pc.parent_id,p.active,p.ean13,q.id,q.qty
            order by p.ean13
        )""" % (self._table, ))


