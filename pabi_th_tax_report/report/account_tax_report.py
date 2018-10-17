# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class AccountTaxReport(models.Model):
    _name = 'account.tax.report'
    _description = 'Account Tax Report (pdf/xls)'
    _auto = False

    doc_type = fields.Selection(
        [('sale', 'Sales'),
         ('purchase', 'Purchase')],
        string='Type',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Move ID',
    )
    move_number = fields.Char(
        string='JE Number',
    )
    move_ref = fields.Char(
        string='JE Ref.',
        help="Original Document",
    )
    year = fields.Char(
        string='Year',
    )
    month = fields.Char(
        string='Month',
    )
    report_period_id = fields.Many2one(
        'account.period',
        string='Reporting Period',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    partner_title = fields.Char(
        string='Partner Title',
    )
    # partner_vat = fields.Char(
    #     string='Partner VAT',
    # )
    # partner_taxbranch = fields.Char(
    #     string='Partner Taxbranch',
    # )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
    )
    tax_sequence = fields.Integer(
        string='Sequence',
    )
    tax_sequence_display = fields.Char(
        string='Sequence Display',
    )
    invoice_date = fields.Date(
        string='Invoice Date',
    )
    invoice_number = fields.Char(
        string='Invoice Number',
    )
    base = fields.Float(
        string='Base',
    )
    amount = fields.Float(
        string='Tax',
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
    )
    number_preprint = fields.Char(
        string='Preprinted Number',
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Responsible',
    )
    validate_user_id = fields.Many2one(
        'res.users',
        related='move_id.validate_user_id',
        string='Validated By',
    )

    def _select(self):
        # res = """
        #     doc_type, atd.id, atd.period_id, am.id as move_id,
        #     am.write_uid as write_uid,
        #     am.name as move_number, am.ref as move_ref,
        #     to_char(ap.date_start, 'YYYY') as "year",
        #     to_char(ap.date_start, 'MM') as "month",
        #     report_period_id, tax_sequence, tax_id, tax_sequence_display,
        #     invoice_date, invoice_number, atd.partner_id,
        #     case when cancel is true then ''
        #         else rp.name end as partner_name,
        #     case when cancel is true then ''
        #         else rpt.name end as partner_title,
        #     case when cancel is true then ''
        #         else rp.vat end as vat,
        #     case when cancel is true then ''
        #         else rp.taxbranch end as taxbranch,
        #     case when cancel is true then 0.0
        #         else base_company end as base,
        #     case when cancel is true then 0.0
        #         else amount_company end as amount,
        #     atd.taxbranch_id, number_preprint
        # """
        res = """
            doc_type, atd.id, atd.period_id, am.id as move_id,
            am.write_uid as write_uid,
            am.name as move_number, am.ref as move_ref,
            to_char(ap.date_start, 'YYYY') as "year",
            to_char(ap.date_start, 'MM') as "month",
            report_period_id, tax_sequence, tax_id, tax_sequence_display,
            invoice_date, invoice_number, atd.partner_id,
            rp.name as partner_name,
            rpt.name as partner_title,
            rp.vat as vat,
            rp.taxbranch as taxbranch,
            base_company as base,
            amount_company as amount,
            atd.taxbranch_id, number_preprint
        """
        return res

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select %s
            from account_tax_detail atd
            left outer join res_partner rp on rp.id = atd.partner_id
            left outer join res_partner_title rpt on rp.title = rpt.id
            left outer join account_period ap on atd.period_id = ap.id
            left outer join account_move am on am.id = atd.ref_move_id
            where report_period_id is not null
            order by year, month, tax_sequence, id
        )""" % (self._table, self._select(), )
        )
