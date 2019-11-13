# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiStockBalance(models.TransientModel):
    _name = 'xlsx.report.pabi.stock.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Location',
     
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
    )
    # date_to = fields.Date(
    #     string='To Date',
    #     required=True,
    # )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.stock.balance.results',
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
        Result = self.env['xlsx.report.pabi.stock.balance.results']
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
        self.results = Result.search(dom)
    


class XLSXReportPabiStockBalanceResults(models.Model):
    _name = 'xlsx.report.pabi.stock.balance.results'
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


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT row_number() over (order by q.product_id) as id,
            t.name as product_name,
            q.product_id as product_id,
            p.default_code as product_code,
            q.location_id as loc_id,
            sl.name as location_name, 
            sum(q.qty) as balance,
            COALESCE((
            select value_float from ir_property where res_id = concat('product.template,',t.id) 
                and type='float' order by id desc limit 1 ) * sum(q.qty),0.0) as price,
            puom.name as uom,
            ou.name as ou_name,
            rc.name as currency,
            (SELECT id from res_org WHERE operating_unit_id = ou.id) as org_id,
            pc.id category_id,
            pc.name as category_name,
            pc.parent_id parent_id
            FROM public.stock_quant q
            left join stock_location sl on q.location_id = sl.id
            left join operating_unit ou on sl.operating_unit_id = ou.id 
            left join product_product p on q.product_id = p.id 
            left join product_template t on p.product_tmpl_id = t.id
            left join product_uom puom on t.uom_id = puom.id
            left join res_company com on com.id = t.company_id
            left join res_currency rc on com.currency_id = rc.id
            left join product_category pc on pc.id = t.categ_id
            group by t.id, sl.name, q.product_id, puom.name, ou.id, ou.name, rc.name, p.default_code, q.location_id,pc.id,pc.name,pc.parent_id 
            order by t.name
        )""" % (self._table, ))







    '''def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        with uitstock as (
            select t.name product,
            sum(product_qty) sumout,
            COALESCE(
            (
	    select value_float from ir_property where res_id = concat('product.template,',t.id) and type='float' order by id desc limit 1  
            ) * sum(product_qty)
            ,0.0) as priceout,
            m.product_id,
            p.default_code,
            m.product_uom,
            ou.name as ou_name,
            puom.name as uom_name,
            m.location_id as loc,
            sl.name as loc_name,
            rc.name as currency,
            (
                SELECT id from res_org WHERE operating_unit_id = ou.id
            ) as org_id
            from stock_move m 
            left join stock_location sl on m.location_id = sl.id
            left join operating_unit ou on sl.operating_unit_id = ou.id 
            left join product_product p 
            on m.product_id = p.id 
            left join product_template t 
            on p.product_tmpl_id = t.id
            left join product_uom puom on t.uom_id = puom.id
            left join res_company com on com.id = t.company_id
            left join res_currency rc on com.currency_id = rc.id
            where m.state like 'done' 
            and m.location_id in (select id from stock_location where operating_unit_id > 0) 
            and m.location_dest_id not in (select id from stock_location where operating_unit_id > 0) 
            group by t.id,product_id,product_uom, t.name, m.location_id, sl.name, p.default_code, puom.name, rc.name, ou.name, ou.id order by t.name asc ) ,
            instock as ( 
            select 
            COALESCE((select price_unit from purchase_order_line where product_id = m.product_id order by id desc limit 1), 00) purchaseprice,
            COALESCE(
            (
	    select value_float from ir_property where res_id = concat('product.template,',t.id) and type = 'float' order by id desc limit 1  
            ) * sum(product_qty)
            ,0.0) as pricein,
            t.name product, 
            sum(product_qty) sumin,
            m.product_id,
            p.default_code,
            puom.name as uom_name,
            ou.name as ou_name,
            m.location_dest_id as loc,
            rc.name as currency,
            sl.name as loc_name,
            (
                SELECT id from res_org WHERE operating_unit_id = ou.id
            ) as org_id
            from stock_move m 
            left join stock_location sl on m.location_dest_id = sl.id 
            left join operating_unit ou on sl.operating_unit_id = ou.id 
            left join product_product p on m.product_id = p.id 
            left join product_template t on p.product_tmpl_id = t.id 
            left join product_uom puom on t.uom_id = puom.id
            left join res_company com on com.id = t.company_id
            left join res_currency rc on com.currency_id = rc.id
            where m.state like 'done' and m.location_id not in (
            select id from stock_location where operating_unit_id > 0) 
            and m.location_dest_id in (select id from stock_location where operating_unit_id > 0) 
            group by t.id,product_id,product_uom, t.name, location_dest_id, sl.name, p.default_code, puom.name,rc.name, ou.name, ou.id order by t.name asc) 
            
            select
            row_number() over (order by i.product) as id,
            i.product as product_name, 
            i.product_id as product_id,
            i.default_code as product_code, 
            i.loc as loc_id,
            u.loc as loc_dest_id,
            coalesce(i.loc_name,u.loc_name) as location_name,
            coalesce(i.ou_name,u.ou_name) as ou_name,
            sumin-coalesce(sumout,0) AS balance, 
            pricein-coalesce(priceout,0) AS price,
            coalesce(i.uom_name,u.uom_name) as uom,
            coalesce(i.currency,u.currency) as currency,
            coalesce(i.org_id,u.org_id) as org_id
            from uitstock u 
            full outer join instock i on u.product = i.product AND u.loc = i.loc
            order by product_code,product_name
        )""" % (self._table, ))'''
