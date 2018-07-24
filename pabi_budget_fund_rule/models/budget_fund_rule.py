# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.tools import float_round as round
from openerp.exceptions import ValidationError


class BudgetFundExpenseGroup(models.Model):
    _name = 'budget.fund.expense.group'
    _description = 'Expense Group'

    name = fields.Char(
        string='Name',
        copy=False,
    )


class BudgetFundRule(models.Model):
    _name = 'budget.fund.rule'
    _inherit = 'mail.thread'

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
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    planned_budget = fields.Float(
        string='Planned Budget',
        compute='_compute_total_budget',
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    template_id = fields.Many2one(
        'budget.fund.rule',
        string='Template',
        domain="[('template', '=', True), ('fund_id', '=', fund_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    fund_rule_line_ids = fields.One2many(
        'budget.fund.rule.line',
        'fund_rule_id',
        string='Spending Rules',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True,
        help="Spending rule for activity groups",
    )
    asset_rule_line_ids = fields.One2many(
        'budget.asset.rule.line',
        'fund_rule_id',
        string='Max Asset Price',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=True,
        help="Maxmimum amount allow on each asset purchase",
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('cancel', 'Cancelled'),
         ],
        string='Status',
        readonly=True,
        index=True,
        copy=False,
        default='draft',
        track_visibility='onchange',
    )

    @api.multi
    def _compute_total_budget(self):
        for rec in self:
            expenses = rec.project_id.summary_expense_ids
            rec.planned_budget = sum(expenses.mapped('planned_amount'))

    @api.multi
    @api.constrains('project_id', 'template')
    def _check_project_template(self):
        for rec in self:
            if rec.template and rec.project_id:
                raise ValidationError(
                    _('This is a template rule, no project allowed!'))
            if not rec.template and not rec.project_id:
                raise ValidationError(
                    _('This is a project rule, template must not checked!'))

    @api.multi
    def action_confirm(self):
        for rec in self:
            for line in rec.fund_rule_line_ids:
                if not line.amount_init:
                    line.amount_init = line.amount
        self.write({'state': 'confirmed'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    @api.constrains('name', 'template', 'fund_id', 'project_id', 'active')
    def _check_unique(self):
        for rec in self:
            if rec.template:
                if len(self.search([('template', '=', True),
                                    ('name', '=', rec.name),
                                    ('fund_id', '=', rec.fund_id.id)])) > 1:
                    raise ValidationError(_('Duplicated Template Name'))
            else:
                if len(self.search([('template', '=', False),
                                    ('project_id', '=', rec.project_id.id),
                                    ('fund_id', '=', rec.fund_id.id),
                                    ('state', '!=', 'cancel')])) > 1:
                    raise ValidationError(_('Duplicated Fund Rule'))

    @api.one
    @api.constrains('fund_rule_line_ids')
    def _check_fund_rule_line_ids(self):
        account_ids = []
        for line in self.fund_rule_line_ids:
            if len(set(line.account_ids._ids).
                   intersection(account_ids)) > 0:
                raise ValidationError(_('Duplicated GL Account'))
            else:
                account_ids += line.account_ids._ids

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.fund_id = False
        self.template_id = False

    @api.onchange('fund_id')
    def _onchange_fund_id(self):
        self.template_id = False

    @api.onchange('template_id')
    def _onchange_template_id(self):
        self.fund_rule_line_ids = []
        Line = self.env['budget.fund.rule.line']
        for line in self.template_id.fund_rule_line_ids:
            new_line = Line.new()
            new_line.expense_group_id = line.expense_group_id
            new_line.account_ids = line.account_ids
            new_line.max_spending_percent = line.max_spending_percent
            self.fund_rule_line_ids += new_line

    @api.model
    def create(self, vals):
        fiscalyear_id = self.env['account.fiscalyear'].find()
        if not vals.get('template', False):
            vals['name'] = self.env['ir.sequence'].\
                with_context(fiscalyear_id=fiscalyear_id).\
                get('budget.fund.rule') or '/'
        return super(BudgetFundRule, self).create(vals)

    @api.model
    def _get_matched_fund_rule(self, project_fund_vals):
        """
        Find matched rule for project/fund combination
        - Project not require fund, ignore rule
        - Project require fund, but not found rule, error
        """
        rules = []
        for val in project_fund_vals:
            project_id, fund_id = val[0], val[1]
            project = self.env['res.project'].browse(project_id)
            fund = self.env['res.fund'].browse(fund_id)
            if not project.require_fund_rule:
                continue
            # Find matching rule for this Project + Funding
            rule = self.env['budget.fund.rule'].\
                search([('project_id', '=', project_id),
                        ('fund_id', '=', fund_id),
                        ('template', '=', False),
                        ('state', 'in', ['draft', 'confirmed'])
                        ])
            if len(rule) == 1:
                rules.append(rule)
            elif len(rule) == 0:
                raise ValidationError(
                    _('Fund rule for project %s / fund %s is not ready!') %
                    (project.code, fund.name))
            elif len(rule) > 1:
                raise ValidationError(
                    _('More than 1 rule is found for project %s / fund %s!') %
                    (project.code, fund.name))
        return rules

    @api.model
    def _get_doc_field_combination(self, doc_lines, args):
        combinations = []
        for l in doc_lines:
            val = ()
            for f in args:
                val += (l[f],)
            if False not in val:
                combinations.append(val)
        return list(set(combinations))

    @api.model
    def document_check_fund_spending(self, doc_lines, amount_field='amount'):
        res = {'budget_ok': True,
               'message': False}
        if not doc_lines:
            return res
        budget_ok = True  # Initial flag
        messages = []
        # Project / Fund unique (to find matched fund rules)
        project_fund_vals = self._get_doc_field_combination(doc_lines,
                                                            ['project_id',
                                                             'fund_id'])
        # Find all matching rules for this transaction
        try:
            rules = self._get_matched_fund_rule(project_fund_vals)
            # Check against each rule
            Activity = self.env['account.activity']
            for rule in rules:
                project = rule.project_id
                fund = rule.fund_id
                # 1) If rule is defined for a Project/Fund, Ativity must valid
                rule_activity_ids = []
                for rule_line in rule.fund_rule_line_ids:
                    rule_activity_ids += [x.id for x in rule_line.activity_ids]
                xlines = filter(lambda l:
                                l['project_id'] == project.id and
                                l['fund_id'] == fund.id,
                                doc_lines)
                activity_ids = list(set([x['activity_rpt_id']
                                         for x in xlines]))
                # Only activity in doc_lines that match rule is allowed
                ex_ids = filter(lambda l:
                                l not in rule_activity_ids, activity_ids)
                ex_activities = Activity.browse(ex_ids)
                if ex_activities:
                    budget_ok = False
                    messages.append(
                        _('Selected Activities: %s, '
                          'is not usable for Fund %s') %
                        (', '.join(ex_activities.mapped('display_name')),
                         rule.fund_id.display_name))

                # 2) Pass first test, then check each rule line
                else:
                    for rule_line in rule.fund_rule_line_ids:
                        activity_ids = rule_line.activity_ids._ids
                        xlines = filter(lambda l:
                                        l['project_id'] == project.id and
                                        l['fund_id'] == fund.id and
                                        l['activity_rpt_id'] in activity_ids,
                                        doc_lines)
                        amount = 0.0
                        if amount_field:  # amount_field means precommit check
                            amount = sum(map(lambda l:
                                             l[amount_field], xlines))
                            amount = self.env['account.budget'].\
                                _calc_amount_company_currency(amount)
                            if amount <= 0.00:
                                continue
                        result = \
                            self.check_fund_activity_spending(rule_line.id,
                                                              amount)
                        if budget_ok and not result['budget_ok']:
                            budget_ok = False
                        if not result['budget_ok']:
                            messages.append(result['message'])

        except ValidationError, e:
            budget_ok = False
            messages.append(e[1])
        except Exception:
            raise
        if not budget_ok:
            res = {'budget_ok': False,
                   'message': '\n'.join(messages)}
        return res

    @api.model
    def check_fund_activity_spending(self, fund_rule_line_id, amount):
        res = {'budget_ok': True,
               'message': False}
        rule_line = self.env['budget.fund.rule.line'].browse(fund_rule_line_id)
        if rule_line.fund_rule_id.state in ('draft'):
            res['budget_ok'] = False
            res['message'] = _('Rules of Fund %s / Project %s '
                               'has been set, but still in draft state!') % \
                (rule_line.fund_rule_id.fund_id.name,
                 rule_line.fund_rule_id.project_id.code)
            return res
        max_percent = rule_line.max_spending_percent
        spending_percent = 0.0
        expense_group = rule_line.expense_group_id
        if not rule_line.amount or rule_line.amount <= 0.0:
            res['budget_ok'] = False
            res['message'] = _('No amount has been allocated for '
                               'Expense Group %s!') % (expense_group.name,)
            return res
        # If amount == 0.0, post commit check, amount_consumed is future
        future_amount = amount == 0.0 and rule_line.amount_consumed or \
            rule_line.amount_consumed + amount
        spending_percent = 100.0 * future_amount / rule_line.amount
        if spending_percent > max_percent:
            res['budget_ok'] = False
            res['message'] = _('Amount exceeded maximum spending '
                               'for Expense Group %s!\n'
                               '(%s%% vs %s%%)') % \
                (expense_group.name,
                 round(spending_percent, 2),
                 round(max_percent, 2))
            return res
        return res

    @api.model
    def document_validate_asset_price(self, doc_lines):
        """ This method sum amount by asset and call
            valiate_asset_price() multiple times, combine messages
        :param doc_lines: list of line item, i.e.,
            for asset_rule_line_id 1029 = 1,000
            [{'asset_rule_line_id': 1029, 'amount': 400.00},
             {'asset_rule_line_id': 1029, 'amount': 600.00}]
        :return: dict of result (messages combined)
        """
        res = {'budget_ok': True,
               'message': False}
        if not doc_lines:
            return res
        budget_ok = True  # Initial flag
        messages = []
        asset_ids = filter(lambda l: l,
                           map(lambda l:
                               l.get('asset_rule_line_id', False), doc_lines))
        asset_ids = list(set(asset_ids))  # Remove False
        for a in asset_ids:
            # On each asset in list, get matched lines
            lines = \
                filter(lambda l: l.get('asset_rule_line_id') == a, doc_lines)
            amount = sum([x.get('amount', 0.0) for x in lines])
            result = self.validate_asset_price(a, amount)
            if budget_ok and not result['budget_ok']:
                budget_ok = False
            if not result['budget_ok']:
                messages.append(result['message'])
        if not budget_ok:
            res = {'budget_ok': False,
                   'message': '\n'.join(messages)}
        return res

    @api.model
    def validate_asset_price(self, asset_rule_line_id, amount):
        """ This will be called by PABI Web, simply to check max price """
        res = {'budget_ok': True,
               'message': False}
        amount = self.env['account.budget'].\
            _calc_amount_company_currency(amount)
        asset_rule = self.env['budget.asset.rule.line'].\
            search([('id', '=', asset_rule_line_id)], limit=1)
        if not asset_rule:
            res['budget_ok'] = False
            res['message'] = _(
                'Selected asset not exists in fund rule!')
            return res
        elif asset_rule.fund_rule_id.state != 'confirmed':
            res['budget_ok'] = False
            res['message'] = _(
                'Fund rule for this project is not confirmed!')
            return res
        elif amount > asset_rule.amount_total:
            res['budget_ok'] = False
            res['message'] = _(
                "%s's price (%s) exceed its maximum amount (%s)") % \
                (asset_rule.asset_name,
                 '{:,.2f}'.format(amount),
                 '{:,.2f}'.format(asset_rule.amount_total))
            return res
        return res


class BudgetFundRuleLine(models.Model):
    _name = 'budget.fund.rule.line'
    _rec_name = 'expense_group_id'
    _description = 'Spending Rule specific for Activity Groups'

    fund_rule_id = fields.Many2one(
        'budget.fund.rule',
        string='Funding Rule',
        index=True,
        ondelete='cascade',
    )
    expense_group_id = fields.Many2one(
        'budget.fund.expense.group',
        string='Expense Group',
        required=True,
        ondelete='restrict',
    )
    project_id = fields.Many2one(
        'res.project',
        related='fund_rule_id.project_id',
        string='Project',
    )
    fund_id = fields.Many2one(
        'res.fund',
        related='fund_rule_id.fund_id',
        string='Fund',
    )
    account_ids = fields.Many2many(
        'account.account',
        'fund_rule_line_account_rel',
        'fund_rule_line_id', 'account_id',
        string='Account',
        domain=[('type', '!=', 'view'),
                '|',
                ('user_type.code', 'ilike', 'fixed asset'),
                ('user_type.code', 'ilike', 'expense')],
        required=True,
        help="List only account type in [fixed asset, expense]",
    )
    activity_ids = fields.Many2many(
        'account.activity',
        'fund_rule_line_activity_rel',
        'fund_rule_line_id', 'activity_id',
        string='Activities',
        compute='_compute_activity_ids',
        store=True,
        readonly=True,
    )
    amount_init = fields.Float(
        string='Fund Amount',
        readonly=True,
    )
    amount = fields.Float(
        string='Lock Amount',
        default=0,
    )
    amount_consumed = fields.Float(
        string='Consumed Amount',
        compute='_compute_amount_consumed',
    )
    percent_consumed = fields.Float(
        string='Consumed (%)',
        compute='_compute_amount_consumed',
    )
    max_spending_percent = fields.Integer(
        string='Max Spending (%)',
        default=100.0,
        required=True,
    )

    @api.multi
    def write(self, vals):
        if 'amount' in vals:
            for rec in self:
                if rec.amount_consumed > vals.get('amount'):
                    raise ValidationError(
                        _('Amount must not less than consumed amount!'))
        # Track changes
        fk = 'fund_rule_id'
        track_fields = ['account_ids', 'amount', 'max_spending_percent']
        self.env['pabi.utils'].track_lines(vals, fk, track_fields, self)
        # --
        return super(BudgetFundRuleLine, self).write(vals)

    @api.multi
    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if not rec.fund_rule_id.template and not rec.amount:
                raise ValidationError(_('Funded Amount must not be zero!'))

    @api.multi
    def _compute_amount_consumed(self):
        for rec in self:
            if not rec.activity_ids or not rec.project_id or not rec.fund_id:
                rec.amount_consumed = 0.0
                continue
            self._cr.execute("""
                select sum(case when budget_method = 'expense'
                            then amount else -amount end) as expense
                from budget_consume_report
                where project_id = %s
                    and fund_id = %s
                    and activity_rpt_id in %s
            """, (rec.project_id.id,
                  rec.fund_id.id,
                  rec.activity_ids._ids,))
            cr_res = self._cr.fetchone()
            rec.amount_consumed = cr_res[0]
            rec.percent_consumed = rec.amount and \
                (rec.amount_consumed * 100.00 / rec.amount) or 0.0
        return

    @api.multi
    @api.depends('account_ids')
    def _compute_activity_ids(self):
        Activity = self.env['account.activity']
        for rec in self:
            rec.activity_ids = Activity.search(
                [('account_id', 'in', rec.account_ids.ids)])
        return


class BudgetAssetRuleLine(models.Model):
    _name = "budget.asset.rule.line"
    _description = "Maxmimum amount allow on each purchase"

    fund_rule_id = fields.Many2one(
        'budget.fund.rule',
        string='Funding Rule',
        index=True,
        ondelete='cascade',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        related='fund_rule_id.project_id',
        readonly=True,
        store=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Project',
        related='fund_rule_id.fund_id',
        readonly=True,
        store=True,
    )
    asset_name = fields.Char(
        string='Asset Name',
        required=True,
    )
    amount_total = fields.Float(
        string='Max Purhcase Amount / Time',
        required=True,
    )
