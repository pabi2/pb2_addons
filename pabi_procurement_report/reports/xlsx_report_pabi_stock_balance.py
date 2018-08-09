# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiStockBalance(models.TransientModel):
    _name = 'xlsx.report.pabi.stock.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.stock.balance.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.stock.balance.results']
        dom = [
            '|',
            ('loc_id', '=', self.location_id.id),
            ('loc_dest_id', '=', self.location_id.id),
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
    loc_dest_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
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

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            with uitstock as (
            select t.name product,
            sum(product_qty) sumout,
            m.product_id,
            p.default_code,
            m.product_uom,
            ou.name as ou_name,
            puom.name as uom_name,
            m.location_id as loc,
            sl.name as loc_name,
            rc.name as currency
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
            group by product_id,product_uom, t.name, m.location_id, sl.name, p.default_code, puom.name, rc.name, ou.name order by t.name asc ) ,
            instock as ( 
            select 
            COALESCE((select price_unit from purchase_order_line where product_id = m.product_id order by id desc limit 1), 00) purchaseprice,
            t.name product, 
            sum(product_qty) sumin,
            m.product_id,
            p.default_code,
            puom.name as uom_name,
            ou.name as ou_name,
            m.location_dest_id as loc,
            rc.name as currency,
            sl.name as loc_name
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
            group by product_id,product_uom, t.name, location_dest_id, sl.name, p.default_code, puom.name,rc.name, ou.name order by t.name asc ) 
            
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
            ((sumin-coalesce(sumout,0)) * purchaseprice) as price,
            coalesce(i.uom_name,u.uom_name) as uom,
            coalesce(i.currency,u.currency) as currency
            from uitstock u 
            full outer join instock i on u.product = i.product AND u.loc = i.loc
            order by product_code,product_name
        )""" % (self._table, ))
