# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError
from openerp import tools


class AccountActivityGroup(models.Model):
    _name = 'account.activity.group'
    _description = 'Activity Group'

    name = fields.Char(
        string='Activity Group',
        required=True,
    )
    activity_ids = fields.One2many(
        'account.activity',
        'activity_group_id',
        string='Activities',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '!=', 'view')],
        help="This account has less priority to activitie's account",
    )
    performance_ids = fields.One2many(
        'account.activity.group.performance.view',
        'activity_group_id',
        string='Activity Group Performance',
        help="Plan vs actual per fiscal year for activity group"
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name)',
         'Activity Group must be unique!'),
    ]

    @api.one
    @api.constrains('account_id', 'activity_ids')
    def _check_account_id(self):
        if not self.account_id and \
                self.env['account.activity'].search_count(
                    [('activity_group_id', '=', self.id),
                     ('account_id', '=', False)]) > 0:
            raise UserError(
                _('Please select account in group or in activity!'))


class AccountActivity(models.Model):
    _name = 'account.activity'
    _description = 'Activity'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    name = fields.Char(
        string='Activity',
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '!=', 'view')],
        help="This account has higher priority to group activities's account",
    )
    performance_ids = fields.One2many(
        'account.activity.performance.view',
        'activity_id',
        string='Activity Performance',
        help="Plan vs actual per fiscal year for activity"
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name, activity_group_id)',
         'Activity must be unique per group!'),
    ]

    @api.multi
    def name_get(self):
        result = []
        for activity in self:
            result.append(
                (activity.id,
                 "%s / %s" % (activity.activity_group_id.name or '-',
                              activity.name or '-')))
        return result

    @api.one
    @api.constrains('account_id')
    def _check_account_id(self):
        if not self.account_id and not self.activity_group_id.account_id:
            raise UserError(
                _('Please select account for activity in group %s!' %
                  (self.activity_group_id.name,)))


class PerformanceView(models.AbstractModel):
    _name = 'generic.performance.view'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    amount_plan = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual Amount',
        readonly=True,
        compute='_amount_all',
    )
    amount_balance = fields.Float(
        string='Balance',
        readonly=True,
        compute='_amount_all',
    )

    _performance_view_tempalte = """CREATE or REPLACE VIEW %s as (
            select ap.fiscalyear_id id,
            ap.fiscalyear_id, abl.%s,
            coalesce(sum(planned_amount), 0.0) amount_plan
        from account_period ap
            join account_budget_line abl on ap.id = abl.period_id
            join account_budget ab on ab.id = abl.budget_id
        where ab.latest_version = true and ab.state = 'done'
        group by ap.fiscalyear_id, abl.%s)
    """

    def _create_performance_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._performance_view_tempalte %
            (self._table, field, field))

    @api.multi
    def _amount_all(self):
        for rec in self:
            # Actual Amount
            self._cr.execute("""
                select sum(debit-credit) amount_actual
                from account_move_line aml
                    join account_period ap on ap.id = aml.period_id
                where aml.%s = %s and ap.fiscalyear_id = %s;
            """ % (self._budgeting_level,
                   rec[self._budgeting_level].id, rec.fiscalyear_id.id))
            rec.amount_actual = self._cr.fetchone()[0] or 0.0
            rec.amount_balance = rec.amount_plan - rec.amount_actual


class AccountActivityGroupPerformanceView(PerformanceView, models.Model):
    _name = 'account.activity.group.performance.view'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    _budgeting_level = 'activity_group_id'

    def init(self, cr):
        self._create_performance_view(cr, self._table, 'activity_group_id')


class AccountActivityPerformanceView(PerformanceView, models.Model):
    _name = 'account.activity.performance.view'
    _auto = False

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    _budgeting_level = 'activity_id'

    def init(self, cr):
        self._create_performance_view(cr, self._table, 'activity_id')
