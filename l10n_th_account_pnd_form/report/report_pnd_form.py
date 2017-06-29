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

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )
    wht_sequence_display = fields.Char(
        string='WHT Sequence Display',
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
    )
    supplier_branch_th = fields.Char(
        string='Supplier Branch',
    )
    supplier_branch = fields.Char(
        string='Supplier Branch',
    )
    supplier_name_th = fields.Char(
        string='Supplier Name (TH)',
    )
    supplier_name = fields.Char(
        string='Supplier Name',
    )
    supplier_street = fields.Char(
        string='Supplier Street',
    )
    supplier_street2 = fields.Char(
        string='Supplier Street2',
    )
    supplier_township = fields.Char(
        string='Supplier Township',
    )
    supplier_district = fields.Char(
        string='Supplier District',
    )
    supplier_province = fields.Char(
        string='Supplier Province',
    )
    supplier_zip = fields.Char(
        string='Supplier Zip',
    )
    supplier_country = fields.Char(
        string='Supplier Country',
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
                and res_id = a.title_id),
                a.title) as title_th,
                coalesce((select value
                from ir_translation
                where name = 'res.partner,name'
                and type = 'model' and lang='th_TH'
                and res_id = a.partner_id),
                a.supplier_name) as supplier_name_th
        from (
        select av.id, av.state,
            av.wht_sequence_display,
            av.number,
            av.date_value,
            av.income_tax_form,
            av.wht_period_id,
            av.id as voucher_id,
            av.tax_payer,
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
            case when av.state != 'cancel'
                then -sum(avt.base) else 0.0 end as base_total,
            case when av.state != 'cancel'
                then -sum(avt.amount) else 0.0 end as tax_total
        from account_voucher av
            left outer join account_voucher_tax avt on avt.voucher_id = av.id
            left outer join res_partner rp on rp.id = av.partner_id
            left outer join res_partner_title rt on rt.id = rp.title
            left outer join res_users ru on ru.partner_id = rp.id
            left outer join resource_resource rr on rr.user_id = ru.id
            left outer join hr_employee emp on emp.resource_id = rr.id
            left outer join res_country_township ts on ts.id = rp.township_id
            left outer join res_country_district dt on dt.id = rp.district_id
            left outer join res_country_province pv on pv.id = rp.province_id
            left outer join res_country co on co.id = rp.country_id
        where av.wht_sequence > 0
        group by av.state, av.wht_sequence_display, av.number,
            av.date_value, av.income_tax_form, av.wht_period_id, av.id,
            av.tax_payer, rp.vat, rp.taxbranch, rp.id, rp.name,
            rt.id, rt.name, emp.id, rp.street, rp.street2,
            ts.name, dt.name, pv.name, ts.zip, co.name
        ) a
        order by a.wht_sequence_display
        )""" % (self._table, ))


class ReportPNDFormLine(models.Model):
    _name = 'report.pnd.form.line'
    _description = 'PND Form Line'
    _auto = False

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
    )
    wht_period = fields.Char(
        string='Period',
    )
    date_value = fields.Date(
        string='Value Date',
    )
    tax_percent = fields.Float(
        string='Tax Percent',
    )
    wht_cert_income_type = fields.Char(
        string='Type of Income',
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
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
        select min(avt.id) id,
            av.state,
            avt.voucher_id,
            av.income_tax_form,
            ap.name as wht_period,
            av.date_value, at.amount * 100 as tax_percent,
            avt.wht_cert_income_type, avt.wht_cert_income_desc,
            case when av.state != 'cancel'
                then -sum(avt.base) else 0.0 end as base,
            case when av.state != 'cancel'
                then -sum(avt.amount) else 0.0 end as tax
        from account_voucher av join account_voucher_tax avt
            on avt.voucher_id = av.id and tax_code_type = 'wht'
            join account_tax at on at.id = avt.tax_id
            left outer join account_period ap on ap.id = av.wht_period_id
        where av.wht_sequence > 0
        group by av.wht_period_id, av.income_tax_form, avt.voucher_id,
            ap.name, av.date_value, avt.wht_cert_income_type,
            avt.wht_cert_income_desc, at.amount, av.state
        )""" % (self._table, ))
