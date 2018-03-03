# -*- coding: utf-8 -*-
import time
from openerp import fields, models, api


class BudgetCarryOver(models.Model):
    _name = 'budget.carry.over'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    doctype = fields.Selection(
        [('purchase_request', 'Purchase Request'),
         ('sale_order', 'Sales Order'),
         ('purchase_order', 'Purchase Order'),
         ('employee_expense', 'Expense'), ],
        string='Document Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Carry to Fiscal Year',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    line_ids = fields.One2many(
        'budget.carry.over.line',
        'carry_over_id',
        string='Carry Over Lines',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        default='draft',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(BudgetCarryOver, self).default_get(fields)
        Fiscal = self.env['account.fiscalyear']
        if not res.get('fiscalyear_id', False):
            fiscals = Fiscal.search([
                ('date_start', '>', time.strftime('%Y-%m-%d'))],
                order='date_start')
            if fiscals:
                res['fiscalyear_id'] = fiscals[0].id
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetCarryOver, self).write(vals)
        if 'doctype' in vals or 'fiscalyear_id' in vals:
            self.compute_commit_docs()
        return res

    @api.model
    def create(self, vals):
        res = super(BudgetCarryOver, self).create(vals)
        res.name = '{:03d}'.format(res.id)
        res.compute_commit_docs()
        return res

    @api.multi
    def compute_commit_docs(self):
        """ This method, based on criteria, list all documents with,
        - Doctype as selected
        - commit_amount > 0
        - For PR/PO, no future fiscalyear lines
        """
        doctypes = {
            'purchase_request': ['purchase.request.line',
                                 'purchase_request_line_id'],
            'sale_order': ['sale.order.line', 'sale_line_id'],
            'purchase_order': ['purchase.order.line', 'purchase_line_id'],
            'employee_expense': ['hr.expense.line', 'expense_line_id'],
        }
        for rec in self:
            rec.line_ids.unlink()
            model = doctypes[rec.doctype][0]
            domain = [('commit_amount', '!=', 0.0)]
            if rec.doctype in ('purchase_request', 'purchase_order'):
                domain += ['|', ('fiscalyear_id', '=', False),
                           ('fiscalyear_id.date_start', '<',
                            rec.fiscalyear_id.date_start)]  # No future fy
            docs = self.env[model].search(domain)
            lines = []
            for doc in docs:
                vals = {}
                line_field = doctypes[rec.doctype][1]
                vals = {line_field: doc.id,
                        'commit_amount': doc.commit_amount, }
                lines.append((0, 0, vals))
            rec.write({'line_ids': lines})

    @api.multi
    def action_carry_over(self):
        for rec in self:
            sale_lines = rec.line_ids.mapped('sale_line_id')
            request_lines = \
                rec.line_ids.mapped('purchase_request_line_id')
            expense_lines = rec.line_ids.mapped('expense_line_id')
            purchase_lines = rec.line_ids.mapped('purchase_line_id')
            # All commits
            commits = sale_lines.mapped('budget_commit_ids') + \
                purchase_lines.mapped('budget_commit_ids') + \
                request_lines.mapped('budget_commit_ids') + \
                expense_lines.mapped('budget_commit_ids')
            commits.write({'monitor_fy_id': rec.fiscalyear_id.id})
        self.write({'state': 'done'})


class BudgetCarryOverLine(models.Model):
    _name = 'budget.carry.over.line'

    name = fields.Char(
        string='Document',
        compute='_compute_name',
    )
    carry_over_id = fields.Many2one(
        'budget.carry.over',
        string='Carry Over',
        index=True,
        ondelete='cascade',
    )
    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string='Purchase Request Line',
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sales Order Line',
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
    )
    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
    )
    commit_amount = fields.Float(
        string='Commitment',
    )

    @api.multi
    def _compute_name(self):
        for rec in self:
            doc = rec.expense_line_id or rec.purchase_request_line_id or \
                rec.purchase_line_id or rec.sale_line_id
            rec.name = doc.display_name
