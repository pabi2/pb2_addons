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
        # copy=True,
    )
    budget_revenue_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'revenue')],
        # copy=True,
    )
    budget_expense_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'expense')],
        # copy=True,
    )
    # version = fields.Float(
    #     string='Revision',
    #     readonly=True,
    #     default=0.0,
    #     digits=(2, 1),
    #     help="Indicate revision of the same budget plan. "
    #     "Only latest one is used",
    # )
    # active = fields.Boolean(
    #     string='Current',
    #     readonly=True,
    #     default=True,
    #     # compute='_compute_latest_version',  TODO: determine version
    #     help="Indicate latest revision of the same plan.",
    # )
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
        string='Past Actual',
        compute='_compute_past_future_rolling',
        help="Commitment + Actual for the past months",
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

    @api.multi
    def _get_past_consumed_domain(self):
        self.ensure_one()
        Period = self.env['account.period']
        current_period = Period.find()
        dom = [('fiscalyear_id', '=', self.fiscalyear_id.id),
               ('period_id', '<', current_period.id)]
        return dom

    @api.multi
    def _get_future_plan_amount(self):
        self.ensure_one()
        Period = self.env['account.period']
        period_num = Period.get_num_period_by_period()  # Now
        future_plan = 0.0
        for line in self.budget_expense_line_ids:
            for i in range(period_num, 13):
                future_plan += line['m%s' % (i,)]
        return future_plan

    @api.multi
    @api.depends()
    def _compute_past_future_rolling(self):
        Consume = self.env['budget.consume.report']
        for budget in self:
            # Past
            dom = budget._get_past_consumed_domain()
            budget.past_consumed = sum(Consume.search(dom).mapped('amount'))
            # Future
            budget.future_plan = budget._get_future_plan_amount()
            # Rolling
            budget.rolling = budget.past_consumed + budget.future_plan

    @api.multi
    @api.depends()
    def _compute_release_diff_rolling(self):
        for budget in self:
            amount_diff = budget.released_amount - budget.rolling
            budget.release_diff_rolling = amount_diff

    @api.multi
    def write(self, vals):
        res = super(AccountBudget, self).write(vals)
        for budget in self:
            if budget.budget_level_id.budget_release == 'manual_header':
                if not budget.budget_expense_line_ids:
                    raise ValidationError(
                        _('Budget %s has no expense line!\n'
                          'This operation can not proceed.') % (budget.name,))
                budget.budget_expense_line_ids.write(
                    {'released_amount': 0.0})
                budget.budget_expense_line_ids[0].write(
                    {'released_amount': budget.to_release_amount})
        return res

    @api.multi
    def _compute_released_amount(self):
        for budget in self:
            budget.released_amount = \
                sum(budget.budget_expense_line_ids.mapped('released_amount'))

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

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

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
                if budget.rolling > budget.released_amount:
                    raise ValidationError(
                        _('%s: rolling plan (%s) will exceed '
                          'released amount (%s) after this operation!') %
                        (budget.name_get()[0][1],
                         '{:,.2f}'.format(budget.rolling),
                         '{:,.2f}'.format(budget.released_amount),
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
                            add_field=False,
                            add_res_id=False):
        monitors = resource.monitor_ids.\
            filtered(lambda x: x.fiscalyear_id == fiscal)
        return monitors

    @api.model
    def check_budget(self, fiscal_id, budget_type,
                     budget_level, budget_level_res_id, amount,
                     ext_field=False, ext_res_id=False,):
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
            'message': False, }
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
                                            ext_field=ext_field,
                                            ext_res_id=ext_res_id)
        # Validation
        if not monitors:  # No plan
            res['budget_ok'] = False
            res['message'] = _('%s\n'
                               '[%s] the requested budget is %s,\n'
                               'but there is no budget control for it.') % \
                (fiscal.name, resource.name_get()[0][1],
                 '{:,.2f}'.format(amount))
            return res
        else:  # Current Budget Status
            res['budget_status'].update({
                'planned_amount': monitors[0].planned_amount,
                'released_amount': monitors[0].released_amount,
                'amount_pr_commit': monitors[0].amount_pr_commit,
                'amount_po_commit': monitors[0].amount_po_commit,
                'amount_exp_commit': monitors[0].amount_exp_commit,
                'amount_actual': monitors[0].amount_actual,
                'amount_balance': monitors[0].amount_balance,
            })
        # If amount is False, we don't check.
        if amount is not False and amount > monitors[0].amount_balance:
            res['budget_ok'] = False
            if amount == 0.0:  # 0.0 mean post check
                res['message'] = _('%s\n'
                                   '%s, not enough budget, this transaction '
                                   'will result in ฿%s over budget!') % \
                    (fiscal.name, resource.name_get()[0][1],
                     '{:,.2f}'.format(-monitors[0].amount_balance))
            else:
                res['message'] = _('%s\n'
                                   '%s, remaining budget is %s,\n'
                                   'but the requested budget is %s') % \
                    (fiscal.name, resource.name_get()[0][1],
                     '{:,.2f}'.format(monitors[0].amount_balance),
                     '{:,.2f}'.format(amount))

        if not blevel.is_budget_control:
            res['budget_ok'] = True  # No control, just return information
        return res

    # kittiu: removed
    # @api.model
    # def _set_release_on_ready(self):
    #     release_result = {}
    #     BudgetLine = self.env['account.budget.line']
    #     for rec in self:
    #         budget_lines = BudgetLine.search([('budget_id', '=', rec.id)])
    #         for line in budget_lines:
    #             release_result.update({line.id: line.planned_amount})
    #     return release_result

    # kittiu: removed
    # @api.multi
    # def do_release_budget(self):
    #     Wizard = self.env['budget.release.wizard']
    #     for budget in self:
    #         _, _, is_auto_release = Wizard._get_release_pattern(budget)
    #         if not is_auto_release:
    #             continue
    #         release_result = budget._set_release_on_ready()
    #         budget.budget_line_ids.release_budget_line(release_result)
    #     return True

    # kittiu: removed
    # @api.model
    # def do_cron_release_budget(self):
    #     # TODO: This will update budget release flag very often.
    #     # How can we prevent this?
    #     # - how about write an release date, and do not repeat in a day
    #     _logger.info("Auto Release Budget - Start")
    #     today = fields.Date.context_today(self)
    #     fiscal_id = self.env['account.fiscalyear'].find(today)
    #     budgets = self.search([('fiscalyear_id', '=', fiscal_id)])
    #     _logger.info("=> Budget IDs = %s" % (budgets._ids,))
    #     budgets.do_release_budget()
    #     _logger.info("Auto Release Budget - END")
    #     return True


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
        # Post change in tracking fields, m1, ... , m12
        for rec in self:
            message = self._change_budget_content(rec, vals)
            if message:
                rec.budget_id.message_post(body=message)
        return super(AccountBudgetLine, self).write(vals)

    @api.multi
    @api.depends()
    def _compute_current_period(self):
        Period = self.env['account.period']
        for rec in self:
            if rec.budget_id.budget_level_id.adjust_past_plan:
                rec.current_period = 0
            else:
                rec.current_period = Period.get_num_period_by_period()

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
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([
                rec.m1, rec.m2, rec.m3, rec.m4, rec.m5, rec.m6,
                rec.m7, rec.m8, rec.m9, rec.m10, rec.m11, rec.m12])
            rec.planned_amount = planned_amount
            # If budget release is auto, update to released_amount
            budget_release = rec.budget_id.budget_level_id.budget_release
            if rec.id and budget_release == 'auto':
                self._cr.execute("""
                    update account_budget_line set released_amount = %s
                    where id = %s
                """, (planned_amount, rec.id))

    @api.model
    def _get_budget_level_type_hook(self, budget_line):
        return 'check_budget'

    @api.multi
    def release_budget_line(self, release_result):
        # TODO: release amount must >= actual+commit and <= planned_amount
        for rec in self:
            amount_to_release = release_result.get(rec.id, 0.0)
            rec.write({'released_amount': amount_to_release})
        return

    # Messaging
    @api.model
    def _change_budget_content(self, line, vals):
        _track_fields = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                         'm7', 'm8', 'm9', 'm10', 'm11', 'm12', ]
        if set(_track_fields).isdisjoint(vals.keys()):
            return False
        title = _('Budget amount change(s)')
        message = '<h3>%s</h3><ul>' % title
        # Get the line label
        line_labels = [line.activity_group_id.name,
                       line.activity_id.name]
        line_labels = filter(lambda a: a is not False, line_labels)
        line_label = '/'.join(line_labels)
        for field in _track_fields:
            if field in vals:
                message += _(
                    '<li><b>%s</b>: %s → %s</li>'
                ) % (line_label,
                     '{:,.2f}'.format(line[field]),
                     '{:,.2f}'.format(vals.get(field)), )
                message += '</ul>'
        return message
