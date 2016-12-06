# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError


class PABIARLatePaymentPenalty(models.TransientModel):
    _name = 'pabi.ar.late.payment.penalty'

    type = fields.Selection(
        [('penalty_invoice', 'Create Invoice for Penalty'),
         ('penalty_calculate', 'Penalty Calculation'),
         ],
        string='Type',
        required=True,
        default='penalty_invoice',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    vat_type = fields.Selection(
        [('include', 'Include VAT'),
         ('exclude', 'Exclude VAT')],
        string='VAT Type',
        required=True,
    )
    rate = fields.Float(
        string='Rate (%) 365 days',
        required=True,
    )
    test_move_line_ids = fields.Many2many(
        'account.move.line',
        'pabi_ar_penalty_move_line_rel',
        'wizard_id', 'move_line_id',
        string='Test Invoices',
        domain="""
        [('reconcile_id', '=', False),
         ('debit', '>', 0.0),
         ('date_maturity', '!=', False),
         ('account_id.type', '=', 'receivable'),
         ('partner_id', '=', partner_id)]
        """,
        help="Specify unpaid invoice number for calculation preview",
    )
    test_paid_date = fields.Date(
        string='Test Paid Date',
        help="Specifiy sample date to test calculate for penalty",
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=True,
        default=lambda self: self.env.user.company_id.
        ar_late_payment_penalty_activity_id,
        domain="[('activity_group_ids', 'in', [activity_group_id or 0])]",
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=True,
        default=lambda self: self.env.user.company_id.
        ar_late_payment_penalty_activity_group_id
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonl=True,
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        required=True,
    )
    line_ids = fields.One2many(
        'pabi.ar.late.payment.list',
        'wizard_id',
        string='Penalty Lines',
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.account_id = self.activity_id.account_id

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        lines = self.line_ids.filtered('select').\
            sorted(lambda x: x.amount_penalty, reverse=True)
        if lines:  # Use section with max penalty
            self.section_id = lines[0].section_id
            self.project_id = lines[0].project_id

    @api.onchange('type', 'partner_id', 'vat_type', 'rate',
                  'test_move_line_ids', 'test_paid_date')
    def _onchange_fields(self):
        self.line_ids = []
        if self.type == 'penalty_invoice':
            self._penalty_invoice()
        elif self.type == 'penalty_calculate':
            self._penalty_calculate()

    @api.model
    def _find_best_costcenter(self, move):
        move_lines = move.line_id.\
            filtered(lambda l: l.section_id or l.project_id).\
            sorted(lambda x: x.credit, reverse=True)
        if move_lines:
            return move_lines[0].section_id, move_lines[0].project_id
        else:
            return False, False

    @api.model
    def _penalty_invoice(self):
        if self.partner_id and self.vat_type and self.rate:
            self._cr.execute("""
            select id, date, date_due, date_paid, amount, amount_tax from
            (
                select aml.id, aml.ref, aml.date,
                    aml.date_maturity date_due,
                    aml.debit amount,
                    (select max(aml2.date) date_paid
                        from account_move_line aml2 join account_journal aj
                        on aj.id = aml2.journal_id
                        and aj.type in ('bank', 'cash')
                        where aml2.reconcile_id = aml.reconcile_id),
                    (select coalesce(sum(aml3.credit), 0.0) amount_tax
                        from account_move_line aml3
                        where aml3.move_id = aml.move_id
                        and aml3.account_id in
                            (select account_collected_id
                            from account_tax where type_tax_use = 'sale'))
                from account_move_line aml
                where debit > 0 and date_maturity is not null
                and reconcile_id is not null
                and partner_id = %s
            ) a
            where date_due < date_paid --> Different clause here
            """, (self.partner_id.id,))
            rows = self._cr.dictfetchall()
            self._fill_lines(rows)

    @api.model
    def _penalty_calculate(self):
        if self.partner_id and self.vat_type and self.rate and \
                self.test_move_line_ids and self.test_paid_date:
            self._cr.execute("""
            select id, date, date_due, date_paid, amount, amount_tax from
            (
                select aml.id, aml.ref, aml.date,
                    aml.date_maturity date_due,
                    aml.debit amount,
                    (select max(aml2.date) date_paid
                        from account_move_line aml2 join account_journal aj
                        on aj.id = aml2.journal_id
                        and aj.type in ('bank', 'cash')
                        where aml2.reconcile_id = aml.reconcile_id),
                    (select coalesce(sum(aml3.credit), 0.0) amount_tax
                        from account_move_line aml3
                        where aml3.move_id = aml.move_id
                        and aml3.account_id in
                            (select account_collected_id
                            from account_tax where type_tax_use = 'sale'))
                from account_move_line aml
                where debit > 0 and date_maturity is not null
                and reconcile_id is null  --> Different clause here
                and partner_id = %s
                and id in %s  --> Different clause here
            ) a
            """, (self.partner_id.id, self.test_move_line_ids._ids))
            rows = self._cr.dictfetchall()
            self._fill_lines(rows, test_paid_date=self.test_paid_date)

    @api.model
    def _fill_lines(self, rows, test_paid_date=False):
        Line = self.env['pabi.ar.late.payment.list']
        for row in rows:
            line = Line.new()
            line.select = True
            line.move_line_id = row['id']
            line.date_invoice = row['date']
            line.date_due = row['date_due']
            line.date_paid = test_paid_date or row['date_paid']
            date_due = datetime.strptime(line.date_due, '%Y-%m-%d')
            date_paid = datetime.strptime(line.date_paid, '%Y-%m-%d')
            line.days_late = (date_paid - date_due).days
            line.amount = self.vat_type == 'include' and \
                row['amount'] or row['amount'] - row['amount_tax']
            line.amount_penalty = (self.rate/100/365 *
                                   line.days_late * line.amount)
            line.section_id, line.project_id = \
                self._find_best_costcenter(line.move_line_id.move_id)
            self.line_ids += line


class PABIARLatePaymentList(models.TransientModel):
    _name = 'pabi.ar.late.payment.list'

    wizard_id = fields.Many2one(
        'pabi.ar.late.payment.penalty',
        string='Wizard',
        readonly=True,
    )
    select = fields.Boolean(
        string='Select',
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Invoices',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
    )
    date_due = fields.Date(
        string='Due',
    )
    date_paid = fields.Date(
        string='Paid',
    )
    days_late = fields.Integer(
        string='Late Days',
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )
    amount_penalty = fields.Float(
        string='Amount Penalty',
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        'res.project',
        string='project',
    )
