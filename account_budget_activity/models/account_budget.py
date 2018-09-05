# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp.api import Environment
from openerp.exceptions import except_orm, ValidationError
from .account_activity import ActivityCommon


import logging
_logger = logging.getLogger(__name__)

BUDGET_STATE = [('draft', 'Draft'),
                # ('cancel', 'Cancelled'),
                # ('confirm', 'Confirmed'),
                # ('validate', 'Validated'),
                ('done', 'Controlled')]


class AccountBudget(models.Model):
    _name = "account.budget"
    _inherit = ['mail.thread']
    _description = "Budget"

    BUDGET_LEVEL = {
        'activity_group_id': 'Activity Group',
        # 'activity_id': 'Activity'  # No Activity Level
    }

    BUDGET_LEVEL_MODEL = {
        'activity_group_id': 'account.activity.group',
        # 'activity_id': 'Activity'  # No Activity Level
    }

    BUDGET_LEVEL_TYPE = {
        'check_budget': 'Check Budget',
    }

    name = fields.Char(
        string='Name',
        required=True,
        default="/",
        states={'done': [('readonly', True)]},
    )
    create_date = fields.Datetime(
        readonly=True,
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # validating_user_id = fields.Many2one(
    #     'res.users',
    #     string='Validating User',
    # )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    state = fields.Selection(
        BUDGET_STATE,
        string='Status',
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    budget_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=False,
    )
    budget_revenue_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'revenue')],
        copy=False,
    )
    budget_expense_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'expense')],
        copy=False,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    to_release_amount = fields.Float(
        string='Released Amount',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        compute='_compute_released_amount',
    )
    commit_amount = fields.Float(
        string='Expense Commitment Amount',
        compute='_compute_commit_amount',
    )
    budgeted_revenue = fields.Float(
        string='Total Revenue Budget',
        compute='_compute_budgeted_overall',
        store=True,
        help="All Revenue",
    )
    budgeted_expense = fields.Float(
        string='Total Expense Budget',
        compute='_compute_budgeted_overall',
        store=True,
        help="All Expense",
    )
    budgeted_overall = fields.Float(
        string='Total Budgeted',
        compute='_compute_budgeted_overall',
        store=True,
        help="All Revenue - All Expense",
    )
    budget_level_id = fields.Many2one(
        'account.fiscalyear.budget.level',
        string='Budget Level',
        compute='_compute_budget_level',
        store=True,
    )
    budget_release = fields.Selection(
        [('manual_line', 'Budget Line'),
         ('manual_header', 'Budget Header'),
         ('auto', 'Auto Release as Planned'), ],
        string='Budget Release',
        compute='_compute_budget_level',
        store=True,
    )
    past_consumed = fields.Float(
        string='Past Actuals',
        compute='_compute_past_future_rolling',
        help="Actual for the past months",
    )
    future_plan = fields.Float(
        string='Future Plan',
        compute='_compute_past_future_rolling',
        help="Future plan amount, including this month",
    )
    rolling = fields.Float(
        string='Rolling',
        compute='_compute_past_future_rolling',
        help="Past Actual + Future Plan",
    )
    release_diff_rolling = fields.Float(
        string='Release - Rolling',
        compute='_compute_release_diff_rolling',
        help="Release amount - rolling amount",
    )
    budget_summary_expense_line_ids = fields.One2many(
        'budget.summary',
        'budget_id',
        string='Summary by Activity Group',
        readonly=True,
        domain=[('budget_method', '=', 'expense')],
        help="Summary by Activity Group View",
    )
    budget_summary_revenue_line_ids = fields.One2many(
        'budget.summary',
        'budget_id',
        string='Summary by Activity Group',
        readonly=True,
        domain=[('budget_method', '=', 'revenue')],
        help="Summary by Activity Group View",
    )
    commitment_summary_expense_line_ids = fields.Many2many(
        'budget.commitment.summary',
        compute='_compute_commitment_summary_line_ids',
        readonly=True,
        help="Summary by fiscal year and section",
    )
    commitment_summary_revenue_line_ids = fields.Many2many(
        'budget.commitment.summary',
        compute='_compute_commitment_summary_line_ids',
        readonly=True,
        help="Summary by fiscal year and section",
    )
    remarks = fields.Text(
        string='Remarks',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def trx_budget_required(self, trx):
        """ Determine whether a transaction require user to select budget
        The logic can be extended by other addons.
        return: 1 = required
                0 = not required
                -1 = not eligible (no field in field_list)
        """
        # # If Product or Activity is selected, budget is required.
        # field_list = ['activity_id', 'product_id']
        # try:
        #     for field in field_list:
        #         if trx[field]:
        #             return 1
        #     return 0
        # except Exception:
        #     return -1
        return 1  # Latest decision is, always required

    @api.model
    def budget_eligible_line(self, analytic_journal, line):
        if analytic_journal and line and \
                'activity_group_id' in line and line.activity_group_id:
            return True
        else:
            return False

    @api.multi
    def _get_past_consumed_domain(self):
        self.ensure_one()
        # Period = self.env['account.period']
        # current_period = Period.find()
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id),
               ('budget_method', '=', 'expense'),
               # May says, past actually should include future one
               # ('period_id', '<=', current_period.id),
               ]
        return dom

    @api.multi
    def _budget_expense_lines_hook(self):
        self.ensure_one()
        return self.budget_expense_line_ids

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s%s%s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        return where_str

    @api.multi
    def _get_past_actual_amount(self):
        self.ensure_one()
        # Consume = self.env['budget.consume.report']
        dom = self._get_past_consumed_domain()
        # consumes = Consume.search(dom)
        # amount = sum(consumes.mapped('amount_actual'))
        # Change domain: [('x', '=', 'y')] to where str: x = 'y'
        sql = """
            select coalesce(sum(amount_actual), 0.0) amount_actual
            from budget_consume_report where %s
        """ % self._domain_to_where_str(dom)
        self._cr.execute(sql)
        amount = self._cr.fetchone()[0]
        return amount

    @api.multi
    def _get_future_plan_amount(self):
        if not self:
            return 0.0
        Period = self.env['account.period']
        Fiscal = self.env['account.fiscalyear']
        period_num = 0
        this_period_date_start = Period.find().date_start
        future_plan = 0.0
        self._cr.execute("""
            select distinct fiscalyear_id from account_budget
            where id in %s
        """, (tuple(self.ids), ))
        fiscal_ids = [x[0] for x in self._cr.fetchall()]
        fiscals = Fiscal.browse(fiscal_ids)
        for fiscal in fiscals:
            if fiscal.date_start > this_period_date_start:
                period_num = 0
            elif fiscal.date_stop < this_period_date_start:
                period_num = 12
            else:
                period_num = Period.get_num_period_by_period()
            budgets = self.search([('id', 'in', self.ids),
                                   ('fiscalyear_id', '=', fiscal.id)])
            for budget in budgets:
                expense_lines = budget._budget_expense_lines_hook()
                for line in expense_lines:
                    for i in range(period_num + 1, 13):
                        future_plan += line['m%s' % (i,)]
        return future_plan

    @api.multi
    def _compute_past_future_rolling(self):
        for budget in self:
            # Past
            budget.past_consumed = budget._get_past_actual_amount()
            # Future
            budget.future_plan = budget._get_future_plan_amount()
            # Rolling
            budget.rolling = budget.past_consumed + budget.future_plan

    @api.multi
    def _compute_release_diff_rolling(self):
        for budget in self:
            amount_diff = budget.released_amount - budget.rolling
            budget.release_diff_rolling = amount_diff

    @api.multi
    def write(self, vals):
        res = super(AccountBudget, self).write(vals)
        for budget in self:
            if budget.budget_level_id.budget_release == 'manual_header':
                if vals.get('policy_amount', False) and \
                        not budget.budget_expense_line_ids:
                    budget.write({
                        'budget_expense_line_ids':
                        [(0, 0, {'m1': vals['policy_amount']})]})
                    # raise ValidationError(
                    #     _('Budget %s has no expense line!\n'
                    #     'This operation can not proceed.') % (budget.name,))
                # If policy amount to allocate, but no budget line yet,
                # do not allow, must set release amount to zero (for now)
                if budget.to_release_amount and \
                        not budget.budget_expense_line_ids:
                    raise ValidationError(
                        _('%s has no budget lines!\n'
                          'Not allow to allocate amount.') % budget.name)
                if budget.budget_expense_line_ids:
                    # Refresh all line to zero first
                    budget.budget_expense_line_ids.write(
                        {'released_amount': 0.0})
                    # Then write to the first line
                    budget.budget_expense_line_ids[0].write(
                        {'released_amount': budget.to_release_amount})
        return res

    @api.multi
    def _compute_released_amount(self):
        for budget in self:
            budget.released_amount = \
                sum(budget.budget_expense_line_ids.mapped('released_amount'))

    @api.multi
    def _compute_commit_amount(self):
        for budget in self:
            budget.commit_amount = \
                sum(budget.commitment_summary_expense_line_ids.
                    mapped('all_commit'))

    @api.model
    def _get_budget_level_type_hook(self, budget):
        return 'check_budget'

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_budget_level(self):
        for budget in self:
            budget_level_type = self._get_budget_level_type_hook(budget)
            budget_level = budget.fiscalyear_id.budget_level_ids.filtered(
                lambda l: l.type == budget_level_type)
            budget.budget_level_id = budget_level
            budget.budget_release = budget_level.budget_release

    @api.multi
    @api.depends('budget_line_ids',
                 'budget_revenue_line_ids',
                 'budget_expense_line_ids')
    def _compute_budgeted_overall(self):
        for rec in self:
            amounts = rec.budget_revenue_line_ids.mapped('planned_amount')
            rec.budgeted_revenue = sum(amounts)
            amounts = rec.budget_expense_line_ids.mapped('planned_amount')
            rec.budgeted_expense = sum(amounts)
            rec.budgeted_overall = rec.budgeted_revenue - rec.budgeted_expense

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

    @api.multi
    def _compute_commitment_summary_line_ids(self):
        Commitment = self.env['budget.commitment.summary']
        for budget in self:
            domain = [('fiscalyear_id', '=', budget.fiscalyear_id.id),
                      ('all_commit', '!=', 0.0)]
            budget.commitment_summary_expense_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'expense')])
            budget.commitment_summary_revenue_line_ids = \
                Commitment.search(domain + [('budget_method', '=', 'revenue')])

    @api.multi
    def _validate_budget_level(self, budget_type='check_budget'):
        LEVEL_DICT = self.env['account.budget'].BUDGET_LEVEL
        for budget in self:
            fiscal = budget.fiscalyear_id
            if not fiscal.budget_level_ids:
                raise ValidationError(_('No budget level configured '
                                        'for this fiscal year'))
            budget_level = fiscal.budget_level_ids.\
                filtered(lambda x: x.type == budget_type)[0].budget_level
            if not budget_level:
                raise ValidationError(
                    _('Budget Level is not setup properly'))
            count = len(self.env['account.budget.line'].search(
                [('budget_id', '=', budget.id), (budget_level, '=', False)]))
            if count:
                raise except_orm(
                    _('Budgeting Level Warning'),
                    _('Required budgeting level is %s') %
                    (LEVEL_DICT[budget_level]))

    # @api.multi
    # def budget_validate(self):
    #     self._validate_budget_level()
    #     self.write({
    #         'state': 'validate',
    #         'validating_user_id': self._uid,
    #     })

    @api.multi
    def _validate_plan_vs_release(self):
        for budget in self:
            if budget.budget_level_id.check_plan_with_released_amount:
                budget.invalidate_cache()
                if budget.rolling > budget.released_amount:
                    raise ValidationError(
                        _('%s: rolling plan (%s) will exceed '
                          'released amount (%s) after this operation!') %
                        (budget.display_name,
                         '{:,.2f}'.format(budget.rolling),
                         '{:,.2f}'.format(budget.released_amount),
                         ))
        return True

    @api.multi
    def _validate_release_vs_policy(self):
        for budget in self:
            if budget.budget_level_id.check_release_with_policy_amount:
                if budget.released_amount > budget.policy_amount:
                    raise ValidationError(
                        _('%s: released amount (%s) will exceed '
                          'policy amount (%s) after this operation!') %
                        (budget.display_name,
                         '{:,.2f}'.format(budget.released_amount),
                         '{:,.2f}'.format(budget.policy_amount),
                         ))
        return True

    @api.multi
    def _validate_future_with_commit(self):
        for budget in self:
            if budget.budget_level_id.check_future_with_commit:
                if budget.future_plan < budget.commit_amount:
                    raise ValidationError(
                        _('%s:\n Future plan amount (%s) must not less than '
                          'commitment amount (%s)!') %
                        (budget.display_name,
                         '{:,.2f}'.format(budget.future_plan),
                         '{:,.2f}'.format(budget.commit_amount),
                         ))
        return True

    # @api.multi
    # def budget_confirm(self):
    #     self._validate_budget_level()
    #     self._validate_plan_vs_release()
    #     self.write({'state': 'confirm'})

    @api.multi
    def budget_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    # def budget_cancel(self):
    #     self.write({'state': 'cancel'})

    @api.multi
    def budget_done(self):
        self._validate_budget_level()
        self._validate_plan_vs_release()
        self._validate_release_vs_policy()
        self._validate_future_with_commit()
        self.write({'state': 'done'})

    # ---- BUDGET CHECK ----
    def convert_lines_to_doc_lines(self, lines):
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.iteritems():
                if field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
            result.append(values)
        return result

    @api.model
    def get_fiscal_and_budget_level(self, budget_date=False):
        if not budget_date:
            budget_date = fields.Date.context_today(self)
        Fiscal = self.env['account.fiscalyear']
        fiscal_id = Fiscal.find(budget_date)
        budget_levels = {}
        for level in Fiscal.browse(fiscal_id).budget_level_ids:
            budget_levels[level.type] = level.budget_level
        return (fiscal_id, budget_levels)

    @api.model
    def _get_budget_resource(self, fiscal, budget_type,
                             budget_level, budget_level_res_id):
        LEVEL_DICT = self.env['account.budget'].BUDGET_LEVEL
        MODEL_DICT = self.env['account.budget'].BUDGET_LEVEL_MODEL
        model = MODEL_DICT.get(budget_level, False)
        if not budget_level_res_id:
            field_name = LEVEL_DICT[budget_level]
            raise Warning(_("Field %s is not entered, "
                            "can not check for budget") % (field_name,))
        resource = self.env[model].browse(budget_level_res_id)
        return resource

    @api.model
    def _get_budget_monitor(self, fiscal, budget_type,
                            budget_level, resource,
                            blevel=False, extra_dom=[]):
        """ For budget check, expenses only """
        # Note: Pass performance test (when compare with Search method)
        comodel = resource._fields['monitor_ids'].comodel_name
        inverse = resource._fields['monitor_ids'].inverse_name
        monitors = self.env[comodel].search([(inverse, '=', resource.id),
                                             ('fiscalyear_id', '=', fiscal.id),
                                             ('budget_method', '=', 'expense'),
                                             ] + extra_dom)
        return monitors

    @api.model
    def check_budget(self, fiscal_id, budget_type,
                     budget_level, budget_level_res_id, amount
                     # ext_field=False, ext_res_id=False,
                     ):
        """ Amount must be in company currency only
        If amount = 0.0, will check current balance from monitor report """
        res = {  # current balance, and result after new amount is applied!
            'budget_ok': True,
            'budget_status': {
                'planned_amount': 0.0,
                'released_amount': 0.0,
                'amount_pr_commit': 0.0,
                'amount_po_commit': 0.0,
                'amount_exp_commit': 0.0,
                'amount_actual': 0.0,
                'amount_balance': 0.0, },
            'message': False,
            'force_no_budget_check': False}
        AccountFiscalyear = self.env['account.fiscalyear']
        BudgetLevel = self.env['account.fiscalyear.budget.level']
        fiscal = AccountFiscalyear.browse(fiscal_id)
        blevel = BudgetLevel.search([('fiscal_id', '=', fiscal_id),
                                    ('type', '=', budget_type),
                                    ('budget_level', '=', budget_level)],
                                    limit=1)
        # # Only for expense document, we check for exp_budget_control setup
        # if self._context.get('call_from', '') == 'hr_expense_expense':
        #     if not blevel.exp_budget_control:
        #         return res
        resource = self._get_budget_resource(fiscal, budget_type,
                                             budget_level,
                                             budget_level_res_id)
        monitors = self._get_budget_monitor(fiscal, budget_type,
                                            budget_level, resource,
                                            blevel=blevel)

        # No plan and no control, do nothing
        if not monitors and not blevel.is_budget_control:
            res['budget_ok'] = True
            res['force_no_budget_check'] = True
            return res
        # Validation
        if not monitors:  # No plan
            res['budget_ok'] = False
            res['message'] = _('%s\n'
                               '[%s] No active budget control.') % \
                (fiscal.name, resource.display_name)
            return res
        else:  # Current Budget Status (Performance Tested, faster then SQL)
            res['budget_status'].update({
                'planned_amount': sum(monitors.mapped('planned_amount')),
                'released_amount': sum(monitors.mapped('released_amount')),
                'amount_pr_commit': sum(monitors.mapped('amount_pr_commit')),
                'amount_po_commit': sum(monitors.mapped('amount_po_commit')),
                'amount_exp_commit': sum(monitors.mapped('amount_exp_commit')),
                'amount_actual': sum(monitors.mapped('amount_actual')),
                'amount_balance': sum(monitors.mapped('amount_balance')),
            })
        # If amount is False, we don't check.
        balance = sum(monitors.mapped('amount_balance'))
        if amount is not False and amount > balance:
            res['budget_ok'] = False
            if amount == 0.0:  # 0.0 mean post check
                res['message'] = _('%s\n'
                                   '%s, not enough budget, this transaction '
                                   'will result in %s฿ over budget!') % \
                    (fiscal.name, resource.display_name,
                     '{:,.2f}'.format(-balance))
            else:
                res['message'] = _('%s\n'
                                   '%s, remaining budget is %s,\n'
                                   'but the requested budget is %s') % \
                    (fiscal.name, resource.display_name,
                     '{:,.2f}'.format(balance),
                     '{:,.2f}'.format(amount))

        if self._context.get('force_no_budget_check', False) or \
                not blevel.is_budget_control:
            res['budget_ok'] = True  # No control, just return information
            res['force_no_budget_check'] = True
        return res


class AccountBudgetLinePeriodSplit(models.Model):
    _name = "account.budget.line.period.split"

    budget_line_id = fields.Many2one(
        'account.budget.line',
        string="Budget Line",
        ondelete='cascade',
        required=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string="Period",
    )
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount",
        store=True,
    )
    sequence = fields.Integer(
        string="Sequence",
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

    @api.depends('budget_line_id',
                 'budget_line_id.planned_amount')
    def _compute_amount(self):
        for line in self:
            if line.sequence == 1:
                line.amount = line.budget_line_id.m1
            elif line.sequence == 2:
                line.amount = line.budget_line_id.m2
            elif line.sequence == 3:
                line.amount = line.budget_line_id.m3
            elif line.sequence == 4:
                line.amount = line.budget_line_id.m4
            elif line.sequence == 5:
                line.amount = line.budget_line_id.m5
            elif line.sequence == 6:
                line.amount = line.budget_line_id.m6
            elif line.sequence == 7:
                line.amount = line.budget_line_id.m7
            elif line.sequence == 8:
                line.amount = line.budget_line_id.m8
            elif line.sequence == 9:
                line.amount = line.budget_line_id.m9
            elif line.sequence == 10:
                line.amount = line.budget_line_id.m10
            elif line.sequence == 11:
                line.amount = line.budget_line_id.m11
            elif line.sequence == 12:
                line.amount = line.budget_line_id.m12


class AccountBudgetLine(ActivityCommon, models.Model):
    _name = "account.budget.line"
    _description = "Budget Line"

    charge_type = fields.Selection(  # Prepare for pabi_internal_charge
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the move line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        required=True,
        default='expense',
    )
    budget_id = fields.Many2one(
        'account.budget',
        string='Budget',
        ondelete='cascade',
        index=True,
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        related='budget_id.fiscalyear_id',
        store=True,
        readonly=True,
    )
    budget_release = fields.Selection(
        [('manual_line', 'Budget Line'),
         ('manual_header', 'Budget Header'),
         ('auto', 'Auto Release as Planned'), ],
        string='Budget Release',
        related='budget_id.budget_release',
    )
    current_period = fields.Integer(
        string='Current Period',
        compute='_compute_current_period',
        default=lambda self: self._default_current_period(),
    )
    description = fields.Char(
        string='Description',
    )
    m1 = fields.Float(
        string='Oct',
    )
    m2 = fields.Float(
        string='Nov',
    )
    m3 = fields.Float(
        string='Dec',
    )
    m4 = fields.Float(
        string='Jan',
    )
    m5 = fields.Float(
        string='Feb',
    )
    m6 = fields.Float(
        string='Mar',
    )
    m7 = fields.Float(
        string='Apr',
    )
    m8 = fields.Float(
        string='May',
    )
    m9 = fields.Float(
        string='Jun',
    )
    m10 = fields.Float(
        string='Jul',
    )
    m11 = fields.Float(
        string='Aug',
    )
    m12 = fields.Float(
        string='Sep',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        store=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        readonly=True,
    )
    budget_state = fields.Selection(
        BUDGET_STATE,
        string='Status',
        related='budget_id.state',
        store=True,
    )
    period_split_line_ids = fields.One2many(
        'account.budget.line.period.split',
        'budget_line_id',
        string="Period Split Lines",
        default=lambda self: self._default_period_split_lines(),
    )

    @api.multi
    def write(self, vals):
        for rec in self:
            if not rec.budget_id.budget_level_id.adjust_past_plan:
                x = rec.current_period + 1
                for i in range(1, x):
                    m = 'm%s' % (i,)
                    if m in vals:
                        raise ValidationError(
                            _('Adjusting past plan amount is not allowed!'))
        # # Post change in tracking fields, m1, ... , m12
        # for rec in self:
        #     message = self._change_budget_content(rec, vals)
        #     if message:
        #         rec.budget_id.message_post(body=message)
        return super(AccountBudgetLine, self).write(vals)

    @api.model
    def _get_current_period(self, fiscal, period, adjust_past_plan=True):
        if adjust_past_plan or fiscal.date_start > period.date_start:
            return 0
        elif fiscal.date_stop < period.date_start:
            return 12
        else:
            return self.env['account.period'].get_num_period_by_period()

    @api.multi
    def _compute_current_period(self):
        period = self.env['account.period'].find()
        for rec in self:
            adjust_past_plan = rec.budget_id.budget_level_id.adjust_past_plan
            rec.current_period = \
                self._get_current_period(rec.fiscalyear_id, period,
                                         adjust_past_plan)
        return True

    @api.model
    def _default_current_period(self):
        fiscalyear_id = self._context['default_fiscalyear_id']
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        budget_level_id = self._context['budget_level_id']
        budget_level = \
            self.env['account.fiscalyear.budget.level'].browse(budget_level_id)
        period = self.env['account.period'].find()
        return self._get_current_period(fiscal, period,
                                        budget_level.adjust_past_plan)

    @api.model
    def _default_period_split_lines(self):
        fy = self._context.get('fiscalyear_id', False)
        if not fy:
            budget_date = fields.Date.context_today(self)
            fy = self.env['account.fiscalyear'].find(budget_date)
        period_ids = self.env['account.period'].search(
            [('fiscalyear_id', '=', fy), ('special', '=', False)],
            order="date_start"
        )
        lines = []
        sequence = 1
        for period in period_ids:
            if period.special:
                continue
            vals = {
                'period_id': period.id,
                'amount': 0.0,
                'sequence': sequence,
            }
            lines.append((0, 0, vals))
            sequence += 1
        return lines

    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        budget_lines = env['account.budget.line'].search(
            [('period_split_line_ids', '=', False)])
        for line in budget_lines:
            fy = line.budget_id.fiscalyear_id
            period_ids = env['account.period'].search(
                [('fiscalyear_id', '=', fy.id), ('special', '=', False)],
                order="date_start"
            )
            sequence = 1
            for period in period_ids:
                if period.special:
                    continue
                vals = {
                    'budget_line_id': line.id,
                    'period_id': period.id,
                    'sequence': sequence,
                }
                BudgetPeriodSplit = env['account.budget.line.period.split']
                BudgetPeriodSplit.sudo().create(vals)
                sequence += 1

    @api.multi
    def auto_release_budget(self):
        for rec in self:
            budget_release = rec.budget_id.budget_level_id.budget_release
            if rec.id and budget_release == 'auto':
                self._cr.execute("""
                    update account_budget_line set released_amount = %s
                    where id = %s
                """, (rec.planned_amount, rec.id))

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([
                rec.m1, rec.m2, rec.m3, rec.m4, rec.m5, rec.m6,
                rec.m7, rec.m8, rec.m9, rec.m10, rec.m11, rec.m12])
            rec.planned_amount = planned_amount
            # If budget release is auto, update to released_amount
            rec.auto_release_budget()

    @api.model
    def _get_budget_level_type_hook(self, budget_line):
        return 'check_budget'

    @api.multi
    def release_budget_line(self, release_result):
        for rec in self:
            amount_to_release = release_result.get(rec.id, 0.0)
            if amount_to_release > rec.planned_amount:
                raise ValidationError(
                    _('Release amount exceed planned amount!'))
            rec.write({'released_amount': amount_to_release})
        return

    # # Messaging
    # Kitti U. We have a more computed one in pabi_chartfield module
    # @api.model
    # def _change_budget_content(self, line, vals):
    #     _track_fields = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6',
    #                      'm7', 'm8', 'm9', 'm10', 'm11', 'm12', ]
    #     if set(_track_fields).isdisjoint(vals.keys()):
    #         return False
    #     title = _('Budget amount change(s)')
    #     message = '<h3>%s</h3><ul>' % title
    #     # Get the line label
    #     line_labels = [line.activity_group_id.name,
    #                    line.activity_id.name]
    #     line_labels = filter(lambda a: a is not False, line_labels)
    #     line_label = '/'.join(line_labels)
    #     for field in _track_fields:
    #         if field in vals:
    #             message += _(
    #                 '<li><b>%s</b>: %s → %s</li>'
    #             ) % (line_label,
    #                  '{:,.2f}'.format(line[field]),
    #                  '{:,.2f}'.format(vals.get(field)), )
    #             message += '</ul>'
    #     return message
