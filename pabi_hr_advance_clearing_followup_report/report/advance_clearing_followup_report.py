# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp import tools
from openerp import models, fields, api


class AdvanceClearingFollowupReport(models.Model):
    _name = "advance.clearing.followup.report"
    _description = 'Advance Clearing Followup Report'
    _auto = False

    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string="AV No.",
    )
    date_advance = fields.Date(
        string="AV Date",
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
    employee_code = fields.Char(
        related='employee_id.employee_code',
        string='Emp Code',
    )
    employee_name = fields.Char(
        related='employee_id.name',
        string='Emp Name',
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Org',
    )
    amount_advanced = fields.Float(
        string='AV Amount',
    )
    amount_advanced_disp = fields.Float(
        string='AV Amount',
        related='amount_advanced'
    )
    date_due = fields.Date(
        string='AV Due Date',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )
    customer_invoice_id = fields.Many2one(
        'account.invoice',
        string='RV Doc.',
    )
    date_customer_invoice = fields.Date(
        related='customer_invoice_id.date_invoice',
        string='RV Date',
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='EX Doc.',
    )
    date_expense_accepted = fields.Date(
        related='expense_id.date',
        string='EX Accepted Date',
    )
    supplier_invoice_id = fields.Many2one(
        'account.invoice',
        string='KV Doc.',
    )
    date_supplier_invoice = fields.Date(
        related='supplier_invoice_id.date_invoice',
        string='KV Date',
    )
    amount_credit_advance = fields.Float(
        string='Credit Advance',
    )
    amount_remaining = fields.Float(
        string='Remaining',
    )
    amount_remaining_disp = fields.Float(
        string='Remaining',
        related='amount_remaining',
    )
    advance_used_percent = fields.Float(
        string='AV Used (%)',
        compute='_compute_advance_used_percent',
    )
    date_sla_30days = fields.Date(
        string='SLA 30 Days',
        compute='_compute_date_sla_30days',
    )
    aging_lt_15 = fields.Boolean(
        string='1-15 Days',
        compute='_compute_aging',
    )
    aging_gt_15 = fields.Boolean(
        string='>15 Days',
        compute='_compute_aging',
    )
    responsible_id = fields.Many2one(
        'res.users',
        related='invoice_id.validate_user_id',
        string='Responsible',
    )
    reason = fields.Char(
        related='expense_id.name',
        string='Reason',
    )

    @api.multi
    def _compute_advance_used_percent(self):
        for rec in self:
            if not rec.amount_advanced:
                rec.advance_used_percent = 100
                continue
            ratio = ((rec.amount_advanced - rec.amount_remaining) /
                     rec.amount_advanced)
            rec.advance_used_percent = ratio * 100
        return

    @api.multi
    def _compute_date_sla_30days(self):
        for rec in self:
            if rec.date_expense_accepted:
                date_sla = datetime.strptime(rec.date_expense_accepted,
                                             '%Y-%m-%d')
                date_sla = date_sla + relativedelta(days=+30)
                rec.date_sla_30days = date_sla.strftime('%Y-%m-%d')
        return

    @api.multi
    def _compute_aging(self):
        for rec in self:
            rec.aging_lt_15 = False
            rec.aging_gt_15 = False
            if rec.date_supplier_invoice:
                if rec.date_sla_30days:
                    date_sla = datetime.strptime(rec.date_expense_accepted,
                                                 '%Y-%m-%d')
                    date_inv = datetime.strptime(rec.date_supplier_invoice,
                                                 '%Y-%m-%d')
                    delta = date_sla - date_inv
                    if delta.days >= 1 and delta.days <= 15:
                        rec.aging_lt_15 = True
                    elif delta.days > 15:
                        rec.aging_gt_15 = True

    def _get_sql_view(self):
        sql_view = """
        select row_number() over (order by adv.number, exc.date) as id,
            adv.id advance_expense_id, adv.date date_advance,
            adv.employee_id,
            adv.operating_unit_id,
            adv.amount_advanced, adv.date_due,
            exc.invoice_id as invoice_id,
            case when exc.expense_id is null then exc.invoice_id
                  else null::int end as customer_invoice_id,
            exc.expense_id expense_id,
            case when exc.expense_id is not null then exc.invoice_id
                else null::int end as supplier_invoice_id,
            coalesce(exc.invoiced_amount, 0.0) as amount_credit_advance,
            adv.amount_advanced - coalesce((select sum(invoiced_amount)
                    from hr_expense_clearing
                    where advance_expense_id = exc.advance_expense_id
                    and date <= exc.date), 0.0) as amount_remaining
        from hr_expense_expense adv
        left outer join hr_expense_clearing exc
            on adv.id = exc.advance_expense_id
        order by adv.number, exc.date
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
