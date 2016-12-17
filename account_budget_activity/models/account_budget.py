# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.api import Environment
from openerp.exceptions import except_orm, Warning as UserError
from .account_activity import ActivityCommon


import logging
_logger = logging.getLogger(__name__)

BUDGET_STATE = [('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('confirm', 'Confirmed'),
                ('validate', 'Validated'),
                ('done', 'Done')]


class AccountBudget(models.Model):
    _name = "account.budget"
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
        states={'done': [('readonly', True)]},
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        string='Validating User',
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='Start Date',
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
    )
    budget_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    budget_revenue_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'revenue')],
        copy=True,
    )
    budget_expense_line_ids = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        domain=[('budget_method', '=', 'expense')],
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('account.budget')
    )
    version = fields.Float(
        string='Version',
        readonly=True,
        default=1.0,
        digits=(2, 1),
        help="Indicate revision of the same budget plan. "
        "Only latest one is used",
    )
    latest_version = fields.Boolean(
        string='Current',
        readonly=True,
        default=True,
        # compute='_compute_latest_version',  TODO: determine version
        help="Indicate latest revision of the same plan.",
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    # planned_amount = fields.Float(
    #     string='Planned Amount',
    #     compute='_compute_amount',
    #     digits_compute=dp.get_precision('Account'),
    # )
    released_amount = fields.Float(
        string='Released Amount',
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
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
    def _compute_amount(self):
        for budget in self:
            # planned_amount = 0.0
            released_amount = 0.0
            for line in budget.budget_line_ids:
                # planned_amount += line.planned_amount
                released_amount += line.released_amount
            # budget.planned_amount = planned_amount
            budget.released_amount = released_amount

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
                raise UserError(_('No budget level configured '
                                  'for this fiscal year'))
            budget_level = fiscal.budget_level_ids.\
                filtered(lambda x: x.type == budget_type)[0].budget_level
            if not budget_level:
                raise UserError(_('Budget Level is not setup properly'))
            count = len(self.env['account.budget.line'].search(
                [('budget_id', '=', budget.id), (budget_level, '=', False)]))
            if count:
                raise except_orm(
                    _('Budgeting Level Warning'),
                    _('Required budgeting level is %s') %
                    (LEVEL_DICT[budget_level]))

    @api.multi
    def budget_validate(self):
        self._validate_budget_level()
        self.write({
            'state': 'validate',
            'validating_user_id': self._uid,
        })
        return True

    @api.multi
    def budget_confirm(self):
        self._validate_budget_level()
        self.write({'state': 'confirm'})
        return True

    @api.multi
    def budget_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def budget_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def budget_done(self):
        self.write({'state': 'done'})
        return True

    # New Revision
    @api.multi
    def new_minor_revision(self):
        self.ensure_one()
        budget = self.copy()
        self.latest_version = False
        budget.latest_version = True
        budget.version = self.version + 0.1
        action = self.env.ref('account_budget_activity.'
                              'act_account_budget_view')
        result = action.read()[0]
        dom = [('id', '=', budget.id)]
        result.update({'domain': dom})
        return result

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
        res = {'fiscal_id': fiscal_id}
        for level in Fiscal.browse(fiscal_id).budget_level_ids:
            res[level.type] = level.budget_level
        return res

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
                     ext_field=False, ext_res_id=False):
        res = {'budget_ok': True,
               'message': False, }
        AccountFiscalyear = self.env['account.fiscalyear']
        BudgetLevel = self.env['account.fiscalyear.budget.level']
        fiscal = AccountFiscalyear.browse(fiscal_id)
        blevel = BudgetLevel.search([('fiscal_id', '=', fiscal_id),
                                    ('type', '=', budget_type),
                                    ('budget_level', '=', budget_level)],
                                    limit=1)
        if not blevel.is_budget_control:
            return res

        if self._context.get('call_from', '') == 'hr_expense_expense':
            if not blevel.exp_budget_control:
                return res

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
                               'but there is no budget plan for it.') % \
                (fiscal.name, resource.name_get()[0][1],
                 '{0:,}'.format(amount))
            return res
        if amount > monitors[0].amount_balance:
            res['budget_ok'] = False
            res['message'] = _('%s\n'
                               '[%s] remaining budget is %s,\n'
                               'but the requested budget is %s') % \
                (fiscal.name, resource.name_get()[0][1],
                 '{0:,}'.format(monitors[0].amount_balance),
                 '{0:,}'.format(amount))
        return res

    @api.multi
    def _prepare_budget_release(self, periods):
        self.ensure_one()
        releases = []
        for period in periods:
            from_period = period[0]
            to_period = period[-1]
            planned_amount = 0.0
            released_amount = 0.0
            release = False
            for budget_line in self.budget_line_ids:
                rr = budget_line._prepare_budget_line_release(periods)
                r = filter(lambda r: (r['from_period'] == from_period and
                                      r['to_period'] == to_period), rr)
                planned_amount += r and r[0]['planned_amount']
                released_amount += r and r[0]['released_amount']
                release = release or (r and r[0]['release'] or False)
            line = {'from_period': from_period,
                    'to_period': to_period,
                    'planned_amount': planned_amount,
                    'released_amount': released_amount,
                    'release': release,
                    }
            releases.append(line)
        return releases

    @api.model
    def _set_release_on_ready(self, releases):
        release_result = {}
        for r in releases:
            for i in range(r['from_period'], r['to_period'] + 1):
                release_result.update({'r'+str(i): r['ready'] or r['release']})
        return release_result

    @api.multi
    def do_release_budget(self):
        Wizard = self.env['budget.release.wizard']
        for budget in self:
            _, _, is_auto_release = Wizard._get_release_pattern(budget)
            if not is_auto_release:
                continue
            releases = Wizard._prepare_budget_release_table(budget._name,
                                                            budget.id)
            release_result = self._set_release_on_ready(releases)
            budget.budget_line_ids.release_budget_line(release_result)
        return True

    @api.model
    def do_cron_release_budget(self):
        # TODO: This will update budget release flag very often.
        # How can we prevent this?
        # - how about write an release date, and do not repeat in a day
        _logger.info("Auto Release Budget - Start")
        today = fields.Date.context_today(self)
        fiscal_id = self.env['account.fiscalyear'].find(today)
        budgets = self.search([('fiscalyear_id', '=', fiscal_id)])
        _logger.info("=> Budget IDs = %s" % (budgets._ids,))
        budgets.do_release_budget()
        _logger.info("Auto Release Budget - END")
        return True


class AccountBudgetLinePeriodSplit(models.Model):
    _name = "account.budget.line.period.split"

    budget_line_id = fields.Many2one(
        'account.budget.line',
        string="Budget Line",
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
    company_id = fields.Many2one(
        'res.company',
        related='budget_id.company_id',
        string='Company',
        type='many2one',
        store=True,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        related='budget_id.fiscalyear_id',
        store=True,
        readonly=True,
    )
    m1 = fields.Float(
        string='Oct',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m2 = fields.Float(
        string='Nov',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m3 = fields.Float(
        string='Dec',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m4 = fields.Float(
        string='Jan',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m5 = fields.Float(
        string='Feb',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m6 = fields.Float(
        string='Mar',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m7 = fields.Float(
        string='Apr',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m8 = fields.Float(
        string='May',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m9 = fields.Float(
        string='Jun',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m10 = fields.Float(
        string='Jul',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m11 = fields.Float(
        string='Aug',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m12 = fields.Float(
        string='Sep',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        compute='_compute_released_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )
    budget_state = fields.Selection(
        BUDGET_STATE,
        string='Status',
        related='budget_id.state',
        store=True,
    )
    # Budget release flag
    r1 = fields.Boolean(
        default=False,
        copy=False,
    )
    r2 = fields.Boolean(
        default=False,
        copy=False,
    )
    r3 = fields.Boolean(
        default=False,
        copy=False,
    )
    r4 = fields.Boolean(
        default=False,
        copy=False,
    )
    r5 = fields.Boolean(
        default=False,
        copy=False,
    )
    r6 = fields.Boolean(
        default=False,
        copy=False,
    )
    r7 = fields.Boolean(
        default=False,
        copy=False,
    )
    r8 = fields.Boolean(
        default=False,
        copy=False,
    )
    r9 = fields.Boolean(
        default=False,
        copy=False,
    )
    r10 = fields.Boolean(
        default=False,
        copy=False,
    )
    r11 = fields.Boolean(
        default=False,
        copy=False,
    )
    r12 = fields.Boolean(
        default=False,
        copy=False,
    )
    period_split_line_ids = fields.One2many(
        'account.budget.line.period.split',
        'budget_line_id',
        string="Period Split Lines",
        default=_default_period_split_lines,
    )

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
            planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                  rec.m5, rec.m6, rec.m7, rec.m8,
                                  rec.m9, rec.m10, rec.m11, rec.m12
                                  ])
            rec.planned_amount = planned_amount  # from last year

    @api.multi
    @api.depends('r1', 'r2', 'r3', 'r4', 'r5', 'r6',
                 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', )
    def _compute_released_amount(self):
        for rec in self:
            released_amount = sum([(rec.m1 * rec.r1), (rec.m2 * rec.r2),
                                   (rec.m3 * rec.r3), (rec.m4 * rec.r4),
                                   (rec.m5 * rec.r5), (rec.m6 * rec.r6),
                                   (rec.m7 * rec.r7), (rec.m8 * rec.r8),
                                   (rec.m9 * rec.r9), (rec.m10 * rec.r10),
                                   (rec.m11 * rec.r11), (rec.m12 * rec.r12),
                                   ])
            rec.released_amount = released_amount  # from last year

    @api.multi
    def release_budget_line(self, release_result):
        # Always release the former period. I.e, r6 will include r1-r5
        periods = list({int(k[1:]): v
                        for k, v in release_result.iteritems()
                        if v})
        period = periods and max(periods) or 0
        vals = {'r'+str(i+1): (i+1) <= period for i in range(12)}
        for rec in self:
            old_vals = {'r'+str(i+1): rec['r'+str(i+1)] for i in range(12)}
            if old_vals != vals:
                rec.write(vals)
        return

    @api.multi
    def _prepare_budget_line_release(self, periods):
        self.ensure_one()
        releases = []
        if not periods:
            return []
        for period in periods:
            from_period = period[0]
            to_period = period[-1]
            release = self['r'+str(to_period)]
            planned_amount = 0.0
            released_amount = 0.0
            for i in period:
                planned_amount += self['m'+str(i)]
                released_amount += self['r'+str(i)] and self['m'+str(i)] or 0.0
            line = {'from_period': from_period,
                    'to_period': to_period,
                    'planned_amount': planned_amount,
                    'released_amount': released_amount,
                    'release': release,
                    }
            releases.append(line)
        return releases
