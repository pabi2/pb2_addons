# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM
from openerp.addons.l10n_th_account.models.account_voucher \
    import TAX_PAYER


class ReportPNDForm(models.Model):
    _name = 'report.pnd.form'
    _description = 'PND Form'
    _auto = False

    cert_id = fields.Many2one(
        'account.wht.cert',
        string='Cert',
    )
    wht_sequence_display = fields.Char(
        string='WHT Sequence Display',
        size=10,
    )
    date_value = fields.Date(
        string='Date Value',
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
    )
    wht_period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    supplier_taxid = fields.Char(
        string='Supplier TaxID',
        size=20,
    )
    supplier_branch_th = fields.Char(
        string='Supplier Branch',
        size=500,
    )
    supplier_branch = fields.Char(
        string='Supplier Branch',
        size=500,
    )
    supplier_name_th = fields.Char(
        string='Supplier Name (TH)',
        size=500,
    )
    supplier_name = fields.Char(
        string='Supplier Name',
        size=500,
    )
    supplier_street = fields.Char(
        string='Supplier Street',
        size=500,
    )
    supplier_street2 = fields.Char(
        string='Supplier Street2',
        size=500,
    )
    supplier_township = fields.Char(
        string='Supplier Township',
        size=500,
    )
    supplier_district = fields.Char(
        string='Supplier District',
        size=500,
    )
    supplier_province = fields.Char(
        string='Supplier Province',
        size=500,
    )
    supplier_zip = fields.Char(
        string='Supplier Zip',
        size=500,
    )
    supplier_country = fields.Char(
        string='Supplier Country',
        size=500,
    )
    tax_payer = fields.Selection(
        TAX_PAYER,
        string='Tax Payer',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        select *, coalesce((select value
                from ir_translation
                where name = 'res.partner.title,name'
                and type = 'model' and lang='th_TH'
                and res_id = a.title_id limit 1),
                a.title) as title_th,
                coalesce((select value
                from ir_translation
                where name = 'res.partner,name'
                and type = 'model' and lang='th_TH'
                and res_id = a.partner_id limit 1),
                a.supplier_name) as supplier_name_th
        from (
        select c.id, c.state,
            c.sequence_display as wht_sequence_display,
            c.number,
            c.date as date_value,
            c.income_tax_form,
            c.period_id as wht_period_id,
            c.id as cert_id,
            c.tax_payer,
            rp.vat as supplier_taxid,
            rp.taxbranch as supplier_branch,
            rp.id as partner_id,
            rp.name as supplier_name,
            rt.id as title_id,
            rt.name as title,
            emp.id as employee_id,
            rp.street as supplier_street,
            rp.street2 as supplier_street2,
            ts.name as supplier_township,
            dt.name as supplier_district,
            pv.name as supplier_province,
            ts.zip as supplier_zip,
            co.name as supplier_country,
            case when c.state != 'cancel'
                then sum(ct.base) else 0.0 end as base_total,
            case when c.state != 'cancel'
                then sum(ct.amount) else 0.0 end as tax_total
        from account_wht_cert c
            left outer join wht_cert_tax_line ct on ct.cert_id = c.id
            left outer join res_partner rp on rp.id = c.supplier_partner_id
            left outer join res_partner_title rt on rt.id = rp.title
            left outer join res_users ru on ru.partner_id = rp.id
            left outer join resource_resource rr on rr.user_id = ru.id
            left outer join hr_employee emp on emp.resource_id = rr.id
            left outer join res_country_township ts on ts.id = rp.township_id
            left outer join res_country_district dt on dt.id = rp.district_id
            left outer join res_country_province pv on pv.id = rp.province_id
            left outer join res_country co on co.id = rp.country_id
        where c.state != 'draft'
        group by c.state, c.sequence_display, c.number,
            c.date, c.income_tax_form, c.period_id, c.id,
            c.tax_payer, rp.vat, rp.taxbranch, rp.id, rp.name,
            rt.id, rt.name, emp.id, rp.street, rp.street2,
            ts.name, dt.name, pv.name, ts.zip, co.name
        ) a
        order by a.wht_sequence_display
        )""" % (self._table, ))


class ReportPNDFormLine(models.Model):
    _name = 'report.pnd.form.line'
    _description = 'PND Form Line'
    _auto = False

    cert_id = fields.Many2one(
        'account.wht.cert',
        string='Cert',
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
    )
    wht_period = fields.Char(
        string='Period',
        size=10,
    )
    date_value = fields.Date(
        string='Value Date',
    )
    tax_percent = fields.Float(
        string='Tax Percent',
    )
    wht_cert_income_type = fields.Char(
        string='Type of Income',
        size=500,
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
        size=500,
    )
    base = fields.Float(
        string='Base',
    )
    tax = fields.Float(
        string='Tax',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        select min(ct.id) id,
            c.state,
            ct.cert_id,
            c.income_tax_form,
            ap.name as wht_period,
            c.date as date_value,
            case when sum(ct.base) != 0 then
                round(sum(ct.amount)/sum(ct.base)*100) else 0.0 end
                as tax_percent,
            ct.wht_cert_income_type, ct.wht_cert_income_desc,
            case when c.state != 'cancel'
                then sum(ct.base) else 0.0 end as base,
            case when c.state != 'cancel'
                then sum(ct.amount) else 0.0 end as tax
        from account_wht_cert c join wht_cert_tax_line ct
            on ct.cert_id = c.id
            left outer join account_period ap on ap.id = c.period_id
        where c.state != 'draft'
        group by c.period_id, c.income_tax_form, ct.cert_id,
            ap.name, c.date, ct.wht_cert_income_type,
            ct.wht_cert_income_desc, c.state
        )""" % (self._table, ))
        
class ReportPnd1aForm(models.Model):
    _name = 'report.pnd1a.form'
    _description = 'PND1A form'
    _auto = False
     
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner ID',
    )
    supplier_taxid = fields.Char(
        string='Supplier TaxID',
        size=20,
    )
    supplier_branch = fields.Char(
        string='Supplier Branch',
        size=500,
    )
    title_th = fields.Char(
        string='Title (TH)',
        size=500,
    )
    supplier_name_th = fields.Char(
        string='Supplier Name (TH)',
        size=500,
    )
    supplier_street = fields.Char(
        string='Supplier Street',
        size=500,
    )
    supplier_street2 = fields.Char(
        string='Supplier Street2',
        size=500,
    )
    supplier_township = fields.Char(
        string='Supplier Township',
        size=500,
    )
    supplier_district = fields.Char(
        string='Supplier District',
        size=500,
    )
    supplier_province = fields.Char(
        string='Supplier Province',
        size=500,
    )
    supplier_zip = fields.Char(
        string='Supplier Zip',
        size=500,
    )
    supplier_country = fields.Char(
        string='Supplier Country',
        size=500,
    )
    calendar_year = fields.Char(
        string='Calendar Year',
    )
    amount_income = fields.Float(
        string='Amount Income',
    )
    amount_wht = fields.Float(
        string='Amount Wht',
    )
     
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT a.partner_id,
        a.supplier_taxid,
        a.supplier_branch,
        COALESCE(( SELECT ir_translation.value
        FROM ir_translation
        WHERE (((ir_translation.name) = 'res.partner.title,name') 
        AND ((ir_translation.type) = 'model') 
        AND ((ir_translation.lang) = 'th_TH') 
        AND (ir_translation.res_id = a.title_id))
        LIMIT 1), (a.title)) AS title_th,
        COALESCE(( SELECT ir_translation.value
        FROM ir_translation
        WHERE (((ir_translation.name) = 'res.partner,name') 
        AND ((ir_translation.type) = 'model') 
        AND ((ir_translation.lang) = 'th_TH') 
        AND (ir_translation.res_id = a.partner_id))
        LIMIT 1), (a.supplier_name)) AS supplier_name_th,
        a.supplier_street,
        a.supplier_street2,
        a.supplier_township,
        a.supplier_district,
        a.supplier_province,
        a.supplier_zip,
        a.supplier_country,
        taxy.calendar_year,
        taxy.amount_income,
        taxy.amount_wht
        FROM (( SELECT rp.vat AS supplier_taxid,
            rp.taxbranch AS supplier_branch,
            rp.id AS partner_id,
            rp.name AS supplier_name,
            rt.id AS title_id,
            rt.name AS title,
            rp.street AS supplier_street,
            rp.street2 AS supplier_street2,
            ts.name AS supplier_township,
            dt.name AS supplier_district,
            pv.name AS supplier_province,
            ts.zip AS supplier_zip,
            co.name AS supplier_country
           FROM ((((((personal_income_tax_yearly pt
             LEFT JOIN res_partner rp ON ((rp.id = pt.partner_id)))
             LEFT JOIN res_partner_title rt ON ((rt.id = rp.title)))
             LEFT JOIN res_country_township ts ON ((ts.id = rp.township_id)))
             LEFT JOIN res_country_district dt ON ((dt.id = rp.district_id)))
             LEFT JOIN res_country_province pv ON ((pv.id = rp.province_id)))
             LEFT JOIN res_country co ON ((co.id = rp.country_id)))) a
             LEFT JOIN personal_income_tax_yearly taxy ON ((taxy.partner_id = a.partner_id)))
            GROUP BY a.partner_id,a.supplier_taxid,a.supplier_branch,a.title_id,a.title,a.supplier_name,
        a.supplier_street,a.supplier_street2,a.supplier_township,a.supplier_district,a.supplier_province,
        a.supplier_zip,a.supplier_country,taxy.calendar_year,taxy.amount_income,taxy.amount_wht
        )""" % (self._table, ))    
