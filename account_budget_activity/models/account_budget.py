# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning as UserError


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
    code = fields.Char(
        string='Code',
        size=16,
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
        string='Responsible User',
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
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'Confirmed'),
         ('validate', 'Validated'),
         ('done', 'Done')],
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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('account.budget')
    )
    version = fields.Integer(
        string='Version',
        readonly=True,
        default=1,
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
            count = self.env['account.budget.line'].search_count(
                [('budget_id', '=', budget.id), (budget_level, '=', False)])
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

    # ---- BUDGET CHECK ----
    @api.model
    def get_fiscal_and_budget_level(self, budget_date=False):
        if not budget_date:
            budget_date = fields.Date.today()
        Fiscal = self.env['account.fiscalyear']
        fiscal_id = Fiscal.find(budget_date)
        res = {'fiscal_id': fiscal_id}
        for level in Fiscal.browse(fiscal_id).budget_level_ids:
            res[level.type] = level.budget_level
        return res

    @api.model
    def _get_budget_resource(self, fiscal, budget_type,
                             budget_level, budget_level_res_id, pu_id=False):
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
                            budget_level, resource, pu_id=False):
        monitors = resource.monitor_ids.\
            filtered(lambda x: x.fiscalyear_id == fiscal)
        return monitors

    @api.model
    def check_budget(self, fiscal_id, budget_type,
                     budget_level, budget_level_res_id, amount, pu_id=False):
        res = {'budget_ok': True,
               'message': False, }
        AccountFiscalyear = self.env['account.fiscalyear']
        fiscal = AccountFiscalyear.browse(fiscal_id)
        if not fiscal.budget_control:
            return res
        resource = self._get_budget_resource(fiscal, budget_type,
                                             budget_level,
                                             budget_level_res_id, pu_id)
        monitors = self._get_budget_monitor(fiscal, budget_type,
                                            budget_level, resource, pu_id)
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


class AccountBudgetLine(models.Model):

    _name = "account.budget.line"
    _description = "Budget Line"

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
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="['|', ('activity_group_id', '=', activity_group_id),"
        "('activity_group_id', '=', False)]"
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        related='budget_id.fiscalyear_id',
        store=True,
        readonly=True,
    )
    m1 = fields.Float(
        string='M1',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m2 = fields.Float(
        string='M2',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m3 = fields.Float(
        string='M3',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m4 = fields.Float(
        string='M4',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m5 = fields.Float(
        string='M5',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m6 = fields.Float(
        string='M6',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m7 = fields.Float(
        string='M7',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m8 = fields.Float(
        string='M8',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m9 = fields.Float(
        string='M9',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m10 = fields.Float(
        string='M10',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m11 = fields.Float(
        string='M11',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m12 = fields.Float(
        string='M12',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            rec.planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                      rec.m5, rec.m6, rec.m7, rec.m8,
                                      rec.m9, rec.m10, rec.m11, rec.m12
                                      ])

    @api.onchange('activity_id')
    def onchange_activity_id(self):
        self.activity_group_id = self.activity_id.activity_group_id
