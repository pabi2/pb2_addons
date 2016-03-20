# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError
from openerp import tools


class MonitorView(models.AbstractModel):
    _name = 'monitor.view'

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

    _monitor_view_tempalte = """CREATE or REPLACE VIEW %s as (
            select ap.fiscalyear_id id,
            ap.fiscalyear_id, abl.%s,
            coalesce(sum(planned_amount), 0.0) amount_plan
        from account_period ap
            join account_budget_line abl on ap.id = abl.period_id
            join account_budget ab on ab.id = abl.budget_id
        where ab.latest_version = true and ab.state in ('validate', 'done')
        group by ap.fiscalyear_id, abl.%s)
    """

    def _create_monitor_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field))

    @api.multi
    def _amount_all(self):
        for rec in self:
            # Actual from move lines (journal = purchase, purchase_refund
            self._cr.execute("""
                select sum(debit-credit) amount_actual
                from account_move_line aml
                    join account_period ap on ap.id = aml.period_id
                where aml.%s = %s and ap.fiscalyear_id = %s
                and journal_id in
                    (select id from account_journal
                    where type in ('purchase', 'purchase_refund'));
            """ % (self._budgeting_level,
                   rec[self._budgeting_level].id, rec.fiscalyear_id.id))
            rec.amount_actual = self._cr.fetchone()[0] or 0.0
            rec.amount_balance = rec.amount_plan - rec.amount_actual

# ------------------ Unit Based ------------------


class ResOrgMonitorView(MonitorView, models.Model):
    _name = 'res.org.monitor.view'
    _auto = False
    _budgeting_level = 'org_id'

    org_id = fields.Many2one(
        'res.org', 'Org', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'org_id')


class ResSectorMonitorView(MonitorView, models.Model):
    _name = 'res.sector.monitor.view'
    _auto = False
    _budgeting_level = 'sector_id'

    sector_id = fields.Many2one(
        'res.sector', 'Sector', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'sector_id')


class ResDivisionGroupMonitorView(MonitorView, models.Model):
    _name = 'res.division.group.monitor.view'
    _auto = False
    _budgeting_level = 'division_group_id'

    division_group_id = fields.Many2one(
        'res.division.group', 'Division Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'division_group_id')


class ResDivisionMonitorView(MonitorView, models.Model):
    _name = 'res.division.monitor.view'
    _auto = False
    _budgeting_level = 'division_id'

    division_id = fields.Many2one(
        'res.division', 'Division', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'division_id')


class ResDepartmentMonitorView(MonitorView, models.Model):
    _name = 'res.department.monitor.view'
    _auto = False
    _budgeting_level = 'department_id'

    department_id = fields.Many2one(
        'res.department', 'Department', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'department_id')


class ResCostcenterMonitorView(MonitorView, models.Model):
    _name = 'res.costcenter.monitor.view'
    _auto = False
    _budgeting_level = 'costcenter_id'

    costcenter_id = fields.Many2one(
        'res.costcenter', 'Costcenter', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'costcenter_id')


# ------------------ Project Based ------------------


class ResSpaMonitorView(MonitorView, models.Model):
    _name = 'res.spa.monitor.view'
    _auto = False
    _budgeting_level = 'spa_id'

    spa_id = fields.Many2one(
        'res.spa', 'SPA', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'spa_id')


class ResMissionMonitorView(MonitorView, models.Model):
    _name = 'res.mission.monitor.view'
    _auto = False
    _budgeting_level = 'mission_id'

    mission_id = fields.Many2one(
        'res.mission', 'Mission', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'mission_id')


class ResProgramSchemeMonitorView(MonitorView, models.Model):
    _name = 'res.program.scheme.monitor.view'
    _auto = False
    _budgeting_level = 'program_scheme_id'

    program_scheme_id = fields.Many2one(
        'res.program.scheme', 'Program Scheme', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_scheme_id')


class ResProgramGroupMonitorView(MonitorView, models.Model):
    _name = 'res.program.group.monitor.view'
    _auto = False
    _budgeting_level = 'program_group_id'

    program_group_id = fields.Many2one(
        'res.program.group', 'Program Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_group_id')


class ResProgramMonitorView(MonitorView, models.Model):
    _name = 'res.program.monitor.view'
    _auto = False
    _budgeting_level = 'program_id'

    program_id = fields.Many2one(
        'res.program', 'Program', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_id')


class ResProjectGroupView(MonitorView, models.Model):
    _name = 'res.project.group.monitor.view'
    _auto = False
    _budgeting_level = 'project_group_id'

    project_group_id = fields.Many2one(
        'res.project.group', 'Project Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'project_group_id')


class ResProjectView(MonitorView, models.Model):
    _name = 'res.project.monitor.view'
    _auto = False
    _budgeting_level = 'project_id'

    project_id = fields.Many2one(
        'res.project', 'Project', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'project_id')
