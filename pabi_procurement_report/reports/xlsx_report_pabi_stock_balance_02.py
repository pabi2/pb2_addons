# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiStockBalance02(models.TransientModel):
    _name = 'xlsx.report.pabi.stock.balance.02'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Location',
        required=True,
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
    results = fields.Many2many(
        'xlsx.report.pabi.stock.balance.results.02',
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

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.stock.balance.results.02']
        dom = []
        if self.location_ids:
            dom += [('loc_id', 'in', self.location_ids.ids)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids.ids)]
        if self.product_ids:
            dom += [('product_id', 'in', self.product_ids.ids)]

        self.results = Result.search(dom)


class XLSXReportPabiStockBalanceResults02(models.Model):
    _name = 'xlsx.report.pabi.stock.balance.results.02'
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
    location_name = fields.Char(
        string='Location Name',
        readonly=True,
    )
    uom_name = fields.Char(
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
            puom.name as uom_name,
            ou.name as ou_name,
            rc.name as currency,
            (SELECT id from res_org WHERE operating_unit_id = ou.id) as org_id
            FROM public.stock_quant q
            left join stock_location sl on q.location_id = sl.id
            left join operating_unit ou on sl.operating_unit_id = ou.id 
            left join product_product p on q.product_id = p.id 
            left join product_template t on p.product_tmpl_id = t.id
            left join product_uom puom on t.uom_id = puom.id
            left join res_company com on com.id = t.company_id
            left join res_currency rc on com.currency_id = rc.id
            group by t.id, sl.name, q.product_id, puom.name, ou.id, ou.name, rc.name, p.default_code, q.location_id
            order by t.name
        )""" % (self._table, ))
