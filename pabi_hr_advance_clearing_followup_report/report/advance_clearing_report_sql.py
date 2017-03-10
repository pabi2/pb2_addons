# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class AdvanceClearingFollowupReport(models.Model):
    _name = "advance.clearing.followup.report.sql"
    _description = 'Advance Clearing Followup Report'
    _auto = False

    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string="Advance Doc No.",
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
    )
    employee_code = fields.Char(
        string="Employee Code",
    )
    employee_name = fields.Char(
        string="Employee Name",
    )
    org_id = fields.Many2one(
        'res.org',
        string="Org.",
    )
    amount_advance = fields.Float(
        string="จำนวนเงินที่ยืม(Amount of loan)",
    )
    date_due = fields.Date(
        string="AV Due Date",
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string="RV Doc No.",
    )
    date_invoice = fields.Date(
        string="RV Posting Date",
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string="EX Doc No.",
    )
    date_valid = fields.Date(
        string="Ex Accepted Date",
    )
    expense_invoice_id = fields.Many2one(
        'account.invoice',
        string="KV Doc No.",
    )
    expense_date_invoice = fields.Date(
        string="KV Posting Date",
    )
    advance_credit = fields.Float(
        string="จำนวนเงิน(Credit Advance)",
    )
    amount_remaining = fields.Float(
        string="ยอดเงินยืมคงเหลือ(Remaining)",
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT
                clearing.id,
                clearing.expense_id as expense_id,
                (SELECT
                    date_valid
                FROM
                    hr_expense_expense
                WHERE
                    id = clearing.expense_id) as date_valid,
                expense.amount as amount_advance,
                (expense.amount-clearing.clearing_amount) as amount_remaining,
                clearing.invoiced_amount as advance_credit,
                clearing.invoice_id as expense_invoice_id,
                (SELECT
                    date_invoice
                FROM
                    account_invoice
                WHERE
                    id = clearing.invoice_id) as expense_date_invoice,
                expense.id as advance_expense_id,
                expense.date_due as date_due,
                expense.invoice_id as invoice_id,
                emp.id as employee_id,
                emp.first_name as employee_name,
                emp.employee_code as employee_code,
                ou.org_id as org_id,
                invoice.date_invoice as date_invoice
            FROM
                hr_expense_clearing clearing
            JOIN hr_expense_expense expense
                ON expense.id = clearing.advance_expense_id
            JOIN hr_employee emp
                ON emp.id = expense.employee_id
            JOIN account_invoice invoice
                ON invoice.id = expense.invoice_id
            JOIN operating_unit ou
                ON ou.id = expense.operating_unit_id
            WHERE clearing.invoice_id is not null
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
