# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import time

class ResPITView(models.Model):
    _name = 'res.pit.view'
    _auto = False


    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
        readonly=True,
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Category',
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        readonly=True,
    )
    customer = fields.Boolean(
        string='Customer',
        readonly=True,
    )
    supplier = fields.Boolean(
        string='Supplier',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY rpb.id) AS id,
                   rp.id AS partner_id, rpb.id AS bank_id, rp.category_id,
                   rp.active, rp.customer, rp.supplier
            FROM res_partner_bank rpb
            LEFT JOIN res_partner rp ON rpb.partner_id = rp.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportPITDetail(models.TransientModel):
    _name = 'xlsx.report.pit.detail'
    _inherit = 'report.account.common'
    


    WHT_CERT_INCOME_TYPE = [('1', '1. เงินเดือน ค่าจ้าง ฯลฯ 40(1)'),
                        ('2', '2. ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)'),
                        ('3', '3. ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)'),
                        ('5', '5. ค่าจ้างทำของ ค่าบริการ ฯลฯ 3 เตรส'),
                        ('6', '6. ค่าบริการ/ค่าสินค้าภาครัฐ'),
                        ('7', '7. ค่าจ้างทำของ ค่ารับเหมา'),
                        ('8', '8. ธุรกิจพาณิชย์ เกษตร อื่นๆ')]


    category_ids = fields.Many2many(
        'res.partner.category',
        string='Categories',
    )
    active = fields.Selection(
        selection=[('true', 'True'), ('false', 'False')],
        string='Active',
    )
    partner_type = fields.Selection(
        [('customer', 'Customer'),
         ('supplier', 'Supplier'),
         ('customer_and_supplier', 'Customer and Supplier'),
         ('customer_or_supplier', 'Customer or Supplier')],
        string='Partner\'s',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
    )
    partner_detail_results = fields.Many2many(
        'res.partner',
        string='Partner Detail Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    income_tax_results = fields.Many2many(
        'personal.income.tax',
        string='personal.income.tax',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    
    @api.multi
    def _get_domain(self):
        """
        Solution
        1. Get all partners (active = true or active = false) by
           default active = true only
        2. Add domain follow criteria as we selected
        """
        self.ensure_one()
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        # Check active
        if self.active == 'true':
            domain += [('active', '=', True)]
        elif self.active == 'false':
            domain += [('active', '=', False)]
        # Check partner type
        if self.partner_type == 'customer_or_supplier':
            domain += ['|', ('customer', '=', True), ('supplier', '=', True)]
        elif self.partner_type == 'customer_and_supplier':
            domain += [('customer', '=', True), ('supplier', '=', True)]
        elif self.partner_type == 'customer':
            domain += [('customer', '=', True)]
        elif self.partner_type == 'supplier':
            domain += [('supplier', '=', True)]
        # Check category
        if self.category_ids:
            domain += [('category_id', 'in', self.category_ids.ids)]
        return domain
    

    @api.onchange('partner_type', 'active', 'category_ids')
    def _onchange_partner_type(self):
        return {'domain': {'partner_ids': self._get_domain()}}
    
    
    @api.multi
    def _get_income_tax_domain(self):
        self.ensure_one()
        domain, number = [], []

        if self.category_ids:
            partner_ids = self.env['res.partner'].search([('category_id', 'in', self.category_ids.ids)])
            pit_ids = self.env['personal.income.tax'].search([('partner_id', 'in', partner_ids.ids)])
            for pit in pit_ids:
                number.append(pit.id)   
        
        if self.partner_ids:
            pit_ids = self.env['personal.income.tax'].search([('partner_id', 'in', self.partner_ids.ids)])
            for pit in pit_ids:
                number.append(pit.id)   
                
        domain += [('id', 'in', number)]   
            
        if not (self.category_ids or self.partner_ids):
            domain = []
        
            
        return domain
            
    @api.multi
    def _compute_results(self):
        self.ensure_one()            
        income_tax = self.env['personal.income.tax']
        income_tax_domain = self._get_income_tax_domain()
        
        self.income_tax_results = income_tax.search(income_tax_domain)


            
            
