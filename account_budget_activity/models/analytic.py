# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class AccountAnalyticJournal(models.Model):
    _inherit = 'account.analytic.journal'

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )

    def init(self, cr):
        # update budget_commit_type for account.exp, as it was noupdate=True
        cr.execute("""
            update account_analytic_journal
            set budget_commit_type = 'actual'
            where id in (select res_id from ir_model_data
                where module = 'account'
                and name in ('exp', 'analytic_journal_sale'))
        """)
        # Update budget_method = Reveue
        cr.execute("""
            update account_analytic_journal
            set budget_method = 'revenue'
            where id = (select res_id from ir_model_data
                where module = 'account'
                and name = 'analytic_journal_sale')
        """)
        # Update budget_method = Expense
        cr.execute("""
            update account_analytic_journal
            set budget_method = 'expense'
            where id = (select res_id from ir_model_data
                where module = 'account'
                and name = 'exp')
        """)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # We don't need, as it can be found from analytic.account.journal
    # budget_method = fields.Selection(
    #     [('revenue', 'Revenue'),
    #      ('expense', 'Expense')],
    #     string='Budget Method',
    #     required=True,
    # )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        compute='_compute_fiscalyear_id',
        store=True,
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    # Don't need as we move to new module
    # doc_id = fields.Reference(
    #     [('purchase.request', 'Purchase Request'),
    #      ('purchase.order', 'Purchase Order'),
    #      ('hr.expense.expense', 'Expense'),
    #      ('account.invoice', 'Invoice')],
    #     string='Doc Ref',
    #     readonly=True,
    # )
    # doc_ref = fields.Char(
    #     string='Doc Ref',
    #     readonly=True,
    # )
    purchase_request_id = fields.Many2one(
        'purchase.request',
        string='Purchase Request',
        readonly=True,
        help="PR Commitment",
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True,
        help="PO Commitment",
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        readonly=True,
        help="SO Commitment",
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
        readonly=True,
        help="Expense Commitment",
    )
    period_id = fields.Many2one(
        'account.period',
        string="Period",
    )
    quarter = fields.Selection(
        [('Q1', 'Q1'),
         ('Q2', 'Q2'),
         ('Q3', 'Q3'),
         ('Q4', 'Q4'),
         ],
        string="Quarter",
        compute="_compute_quarter",
        store=True,
    )

    @api.depends('period_id')
    def _compute_quarter(self):
        for line in self:
            period = line.period_id
            periods = self.env['account.period'].search(
                [('fiscalyear_id', '=', period.fiscalyear_id.id),
                 ('special', '=', False)],
                order="date_start").ids
            period_index = periods.index(period.id)
            if period_index in (0, 1, 2):
                line.quarter = 'Q1'
            elif period_index in (3, 4, 5):
                line.quarter = 'Q2'
            elif period_index in (6, 7, 8):
                line.quarter = 'Q3'
            elif period_index in (9, 10, 11):
                line.quarter = 'Q4'

    @api.multi
    @api.depends('date')
    def _compute_fiscalyear_id(self):
        for rec in self:
            FiscalYear = self.env['account.fiscalyear']
            rec.fiscalyear_id = FiscalYear.find(rec.date)

    @api.model
    def create(self, vals):
        """ Add posting dimension """
        if vals.get('account_id', False):
            Analytic = self.env['account.analytic.account']
            analytic = Analytic.browse(vals['account_id'])
            if not analytic:
                analytic = Analytic.create_matched_analytic(self)
            if analytic:
                domain = Analytic.get_analytic_search_domain(analytic)
                vals.update(dict((x[0], x[2]) for x in domain))
        # Prepare period_id for reporting purposes
        if vals.get('date', False):
            periods = self.env['account.period'].find(vals['date'])
            period = periods and periods[0] or False
            vals.update({'period_id': period.id})
        # --
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            # Prepare period_id for reporting purposes
            if vals.get('date', rec.date):
                date = vals.get('date', rec.date)
                periods = self.env['account.period'].find(date)
                period = periods and periods[0] or False
                vals.update({'period_id': period.id})
            # --
        return super(AccountAnalyticLine, self).write(vals)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(
        [('view', 'Analytic View'),
         ('normal', 'Analytic Account'),
         ('pr_product', 'PR Product'),
         ('product', 'Product'),
         ('activity', 'Activity'),
         ('contract', 'Contract or Project'),
         ('template', 'Template of Contract')]
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        ondelete='restrict',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        ondelete='restrict',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        ondelete='restrict',
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = [
            'product_id',
            'activity_id',
            'activity_group_id',
        ]
        return dimensions

    @api.model
    def get_analytic_search_domain(self, rec):
        dimensions = self._analytic_dimensions()
        domain = []
        for dimension in dimensions:
            domain.append((dimension, '=', rec[dimension].id))
        return domain

    @api.model
    def get_matched_analytic(self, rec):
        domain = self.get_analytic_search_domain(rec)
        if rec._name == 'account.model.line':  # From Recurring Models
            domain.append(('type', '=', 'normal'))
        if rec.product_id:
            domain.append(('type', '=', 'product'))
        elif rec.activity_id:
            domain.append(('type', '=', 'activity'))
        else:  # Last possible type, from Purchase Request
            domain.append(('type', '=', 'pr_product'))
        analytics = self.env['account.analytic.account'].search(domain)
        if analytics:
            return analytics[0]
        return False

    @api.model
    def _invalid_domain(self, domain):
        # If all domain valus is false, it is invalid
        res = list(set([x[2] is False for x in domain]))
        if len(res) == 1 and res[0] is True:
            return True
        return False

    @api.model
    def create_matched_analytic(self, rec):
        # Not allow product and activity at the same time.
        if ('product_id' in rec._fields) and ('activity_id' in rec._fields):
            if rec.product_id and rec.activity_id:
                raise UserError(_('Select both Product and '
                                  'Activity is prohibited'))
        # Only create analytic if not exists yet
        Analytic = self.env['account.analytic.account']
        domain = self.get_analytic_search_domain(rec)
        # If not a valid domain, return False (domain with no values)
        if self._invalid_domain(domain):
            return False
        if rec._name == 'account.model.line':  # Creating from Recurring Entry
            domain.append(('type', '=', 'normal'))
        elif rec.product_id:
            domain.append(('type', '=', 'product'))
        elif rec.activity_id:
            domain.append(('type', '=', 'activity'))
        else:
            domain.append(('type', '=', 'pr_product'))
        analytics = Analytic.search(domain)
        if not analytics:
            vals = dict((x[0], x[2]) for x in domain)
            vals['name'] = (rec.product_id.name or
                            rec.activity_id.name or
                            ('name' in rec and rec.name) or
                            ('product_name' in rec and rec.product_name) or
                            False)
            vals['type'] = ((rec._name == 'account.model.line' and 'normal') or
                            (rec.product_id and 'product') or
                            (rec.activity_id and 'activity') or
                            'pr_product')
            return Analytic.create(vals)
        else:
            return analytics[0]
