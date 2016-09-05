# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError


class BudgetFundRule(models.Model):
    _name = "budget.fund.rule"
    _description = "Rule for Budget's Fund vs Project"

    name = fields.Char(
        string='Number',
        index=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    template = fields.Boolean(
        string='Template',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    template_id = fields.Many2one(
        'budget.fund.rule',
        string='Template',
        domain="[('template', '=', True), ('fund_id', '=', fund_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'fund_rule_fiscalyear_rel',
        'fund_rule_id', 'fiscalyear_id',
        string='Fiscal Years',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fund_rule_line_ids = fields.One2many(
        'budget.fund.rule.line',
        'fund_rule_id',
        string='Spending Rules',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Spending rule for activity groups",
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('acknowledged', 'Acknowledged'),
         ('cancel', 'Cancelled'),
         ],
        string='Status',
        readonly=True,
        index=True,
        copy=False,
        default='draft',
    )

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def action_acknowledge(self):
        self.write({'state': 'acknowledged'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.one
    @api.constrains('name', 'template', 'fund_id', 'project_id')
    def _check_unique(self):
        if self.template:
            if len(self.search([('template', '=', True),
                                ('name', '=', self.name),
                                ('fund_id', '=', self.fund_id.id)])) > 1:
                raise UserError(_('Duplicated Template Name'))
        else:
            if len(self.search([('template', '=', False),
                                ('project_id', '=', self.project_id.id),
                                ('fund_id', '=', self.fund_id.id)])) > 1:
                raise UserError(_('Duplicated Fund Rule'))

    @api.one
    @api.constrains('fund_rule_line_ids',
                    'fund_rule_line_ids.activity_group_ids')
    def _check_fund_rule_line_ids(self):
        activity_group_ids = []
        for line in self.fund_rule_line_ids:
            if len(set(line.activity_group_ids._ids).
                   intersection(activity_group_ids)) > 0:
                raise UserError(_('Duplicated Activity Groups'))
            else:
                activity_group_ids += line.activity_group_ids._ids

    @api.onchange('fund_id')
    def _onchange_fund_id(self):
        self.template_id = False

    @api.onchange('template_id')
    def _onchange_template_id(self):
        self.fund_rule_line_ids = False
        self.fund_rule_line_ids = []
        Line = self.env['budget.fund.rule.line']
        for line in self.template_id.fund_rule_line_ids:
            new_line = Line.new()
            new_line.expense_group = line.expense_group
            new_line.activity_group_ids = line.activity_group_ids
            new_line.max_spending_percent = line.max_spending_percent
            self.fund_rule_line_ids += new_line

    @api.model
    def create(self, vals):
        if not vals.get('template', False):
            vals['name'] = \
                self.env['ir.sequence'].get('budget.fund.rule') or '/'
        return super(BudgetFundRule, self).create(vals)

    @api.model
    def _get_matched_fund_rule(self, project_fund_vals, fiscalyear_id):
        rules = []
        for val in project_fund_vals:
            project_id, fund_id = val[0], val[1]
            # Find matching rule for this Project + Funding
            rule = self.env['budget.fund.rule'].\
                search([('fiscalyear_ids', 'in', [fiscalyear_id]),
                        ('project_id', '=', project_id),
                        ('fund_id', '=', fund_id),
                        ('template', '=', False)])
            if len(rule) == 1:
                rules.append(rule)
            elif len(rule) > 1:
                project = self.env['res.project'].browse(project_id)
                fund = self.env['res.fund'].browse(fund_id)
                raise ValidationError(
                    _('More than 1 rule is found for project %s / fund %s!') %
                    (project.code, fund.name))
        return rules

    @api.model
    def document_check_fund_spending(self, doc_date, doc_lines, amount_field):
        res = {'budget_ok': True,
               'message': False}
        Budget = self.env['account.budget']
        BudgetLevel = self.env['account.fiscalyear.budget.level']
        Fiscal = self.env['account.fiscalyear']
        fiscalyear_id = Fiscal.find(doc_date)
        blevel = BudgetLevel.search([('fiscal_id', '=', fiscalyear_id),
                                    ('type', '=', 'project_base'),
                                    ('budget_level', '=', 'fund_id')], limit=1)
        if not blevel.is_budget_control or \
                not doc_lines:
            return res
        # Project / Fund unique (to find matched fund rules
        project_fund_vals = Budget._get_doc_field_combination(doc_lines,
                                                              ['project_id',
                                                               'fund_id'])
        # Find all matching rules for this transaction
        rules = self._get_matched_fund_rule(project_fund_vals, fiscalyear_id)
        # Check against each rule
        for rule in rules:
            project = rule.project_id
            fund = rule.fund_id
            # 1) If rule is defined for a Project/Fund, AG must be valid
            rule_ag_ids = []
            for rule_line in rule.fund_rule_line_ids:
                rule_ag_ids += [x.id for x in rule_line.activity_group_ids]
            xlines = filter(lambda l:
                            l['project_id'] == project.id and
                            l['fund_id'] == fund,
                            doc_lines)
            ag_ids = [x.activity_group_id.id for x in xlines]
            # Only activity groups in doc_lines that match rule is allowed
            if not (set(ag_ids) < set(rule_ag_ids)):
                res['budget_ok'] = False
                res['message'] = _('Selected Activity Group is '
                                   'not usable for Fund %s') % \
                    (rule.fund_id.name,)
                return res
            # 2) Check each rule line
            for rule_line in rule.fund_rule_line_ids:
                ag_ids = rule_line.activity_group_ids._ids
                xlines = filter(lambda l:
                                l['project_id'] == project.id and
                                l['fund_id'] == fund.id and
                                l['activity_group_id'] in ag_ids,
                                doc_lines)
                amount = sum(map(lambda l: l[amount_field], xlines))
                if amount <= 0.00:
                    continue
                res = self.check_fund_activity_spending(fiscalyear_id,
                                                        project.id,
                                                        fund.id,
                                                        rule_line.id,
                                                        ag_ids,
                                                        amount)
                if not res['budget_ok']:
                    return res
        return res

    @api.model
    def check_fund_activity_spending(self, fiscalyear_id, project_id,
                                     fund_id, fund_rule_line_id,
                                     activity_group_ids, amount):
        res = {'budget_ok': True,
               'message': False}
        rule_line = self.env['budget.fund.rule.line'].browse(fund_rule_line_id)
        if rule_line.fund_rule_id.state in ('draft', 'cancel'):
            res['budget_ok'] = False
            res['message'] = _('Rules of Fund %s / Project %s '
                               'is not yet confirmed!') % \
                (rule_line.fund_rule_id.fund_id.name,
                 rule_line.fund_rule_id.project_id.code)
            return res
        max_percent = rule_line.max_spending_percent
        expense_group = rule_line.expense_group
        self._cr.execute("""
            select
                coalesce(sum(planned_amount), 0.0) as planned_amount,
                coalesce(sum(released_amount), 0.0) as released_amount,
                coalesce(sum(amount_balance), 0.0) as amount_balance
            from budget_monitor_report
            where fiscalyear_id = %s
                and project_id = %s
                and fund_id = %s
                and activity_group_id in %s
        """, (fiscalyear_id, project_id, fund_id, activity_group_ids,))
        cr_res = self._cr.fetchone()
        released_amount = cr_res[1]
        amount_balance = cr_res[2]
        if released_amount <= 0.0 or amount_balance <= 0.0:
            res['budget_ok'] = False
            res['message'] = _('Not enough budget for expense group %s!') % \
                (expense_group,)
            return res
        spending_percent = 100.0 * ((released_amount -
                                     amount_balance +
                                     amount) /
                                    released_amount)
        if spending_percent > max_percent:
            res['budget_ok'] = False
            res['message'] = _('Amount exceeded maximum spending '
                               'for Expense Group %s!\n'
                               '(%s%% vs %s%%)') % \
                (expense_group,
                 round(spending_percent, 2),
                 round(max_percent, 2))
            return res
        return res


class BudgetFundRuleLine(models.Model):
    _name = "budget.fund.rule.line"
    _description = "Spending Rule specific for Activity Groups"

    fund_rule_id = fields.Many2one(
        'budget.fund.rule',
        string='Funding Rule',
        index=True,
        ondelete='cascade',
    )
    expense_group = fields.Char(
        string='Expense Group',
        required=True,
    )
    project_id = fields.Many2one(
        'res.project',
        related='fund_rule_id.project_id',
        string='Project',
        store=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        related='fund_rule_id.fund_id',
        string='Fund',
        store=True,
    )
    activity_group_ids = fields.Many2many(
        'account.activity.group',
        'fund_rule_line_activity_group_rel',
        'fund_rule_line_id', 'activity_group_id',
        string='Activity Groups',
    )
    max_spending_percent = fields.Integer(
        string='Max Spending (%)',
        default=100.0,
        required=True,
    )
