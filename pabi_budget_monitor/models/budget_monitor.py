# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools
from openerp.addons.account_budget_activity.models.budget_monitor \
    import MonitorView


class MonitorViewEx(MonitorView):

    amount_pr_commit = fields.Float(
        string='PR Committed Amount',
        readonly=True,
        compute='_amount_all',
    )

    def _prepare_pr_commit_amount_sql(self):
        """ Commit amount will involce purchase_request """
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - purchased_qty)) amount_commit
        from purchase_request_line line
            join purchase_request doc on line.request_id = doc.id
                and (doc.date_approved is not null
                    and doc.state in ('approved'))
            join account_fiscalyear af
                on (doc.date_approved <= af.date_stop
                    and doc.date_approved >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = doc.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = doc.currency_id)
              AND ((doc.date_approved IS NOT NULL
                      AND cr2.name <= doc.date_approved)
            OR (doc.date_approved IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where line.%s = %s and af.id = %s
        """
        return sql

    @api.model
    def _get_amount_pr_commit(self):
        self._cr.execute(self._prepare_pr_commit_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id))
        return self._cr.fetchone()[0] or 0.0

    @api.multi
    def _amount_all(self):
        """ Overwrite, adding amount_commit """
        for rec in self:
            rec.amount_pr_commit = rec._get_amount_pr_commit()
            rec.amount_po_commit = rec._get_amount_po_commit()
            rec.amount_actual = rec._get_amount_actual()
            # Balance
            rec.amount_balance = (rec.amount_plan -
                                  (rec.amount_pr_commit +
                                   rec.amount_po_commit) -
                                  rec.amount_actual)

# ------------------ Unit Based ------------------


class ResOrgMonitorView(MonitorViewEx, models.Model):
    _name = 'res.org.monitor.view'
    _auto = False
    _budget_level = 'org_id'

    org_id = fields.Many2one(
        'res.org', 'Org', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'org_id')


class ResSectorMonitorView(MonitorViewEx, models.Model):
    _name = 'res.sector.monitor.view'
    _auto = False
    _budget_level = 'sector_id'

    sector_id = fields.Many2one(
        'res.sector', 'Sector', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'sector_id')


class ResDepartmentMonitorView(MonitorViewEx, models.Model):
    _name = 'res.department.monitor.view'
    _auto = False
    _budget_level = 'department_id'

    department_id = fields.Many2one(
        'res.department', 'Department', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'department_id')


class ResDivisionMonitorView(MonitorViewEx, models.Model):
    _name = 'res.division.monitor.view'
    _auto = False
    _budget_level = 'division_id'

    division_id = fields.Many2one(
        'res.division', 'Division', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'division_id')


class ResSectionMonitorView(MonitorViewEx, models.Model):
    _name = 'res.section.monitor.view'
    _auto = False
    _budget_level = 'section_id'

    section_id = fields.Many2one(
        'res.section.group', 'Section', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'section_id')


class ResCostcenterMonitorView(MonitorViewEx, models.Model):
    _name = 'res.costcenter.monitor.view'
    _auto = False
    _budget_level = 'costcenter_id'

    costcenter_id = fields.Many2one(
        'res.costcenter', 'Costcenter', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'costcenter_id')


# ------------------ Tags ------------------

class ResSpaMonitorView(MonitorViewEx, models.Model):
    _name = 'res.spa.monitor.view'
    _auto = False
    _budget_level = 'spa_id'

    spa_id = fields.Many2one(
        'res.spa', 'SPA', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'spa_id')


class ResMissionMonitorView(MonitorViewEx, models.Model):
    _name = 'res.mission.monitor.view'
    _auto = False
    _budget_level = 'mission_id'

    mission_id = fields.Many2one(
        'res.mission', 'Mission', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'mission_id')


class ResTagTypeMonitorView(MonitorViewEx, models.Model):
    _name = 'res.tag.type.monitor.view'
    _auto = False
    _budget_level = 'tag_type_id'

    tag_type_id = fields.Many2one(
        'res.tag.type', 'Tag Type', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'tag_type_id')


class ResTagMonitorView(MonitorViewEx, models.Model):
    _name = 'res.tag.monitor.view'
    _auto = False
    _budget_level = 'tag_id'

    tag_id = fields.Many2one(
        'res.tag', 'Tag', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'tag_id')


# ------------------ Project Based ------------------

class ResProgramSchemeMonitorView(MonitorViewEx, models.Model):
    _name = 'res.program.scheme.monitor.view'
    _auto = False
    _budget_level = 'program_scheme_id'

    program_scheme_id = fields.Many2one(
        'res.program.scheme', 'Program Scheme', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_scheme_id')


class ResProgramGroupMonitorView(MonitorViewEx, models.Model):
    _name = 'res.program.group.monitor.view'
    _auto = False
    _budget_level = 'program_group_id'

    program_group_id = fields.Many2one(
        'res.program.group', 'Program Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_group_id')


class ResProgramMonitorView(MonitorViewEx, models.Model):
    _name = 'res.program.monitor.view'
    _auto = False
    _budget_level = 'program_id'

    program_id = fields.Many2one(
        'res.program', 'Program', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'program_id')


class ResProjectGroupView(MonitorViewEx, models.Model):
    _name = 'res.project.group.monitor.view'
    _auto = False
    _budget_level = 'project_group_id'

    project_group_id = fields.Many2one(
        'res.project.group', 'Project Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'project_group_id')


class ResProjectView(MonitorViewEx, models.Model):
    _name = 'res.project.monitor.view'
    _auto = False
    _budget_level = 'project_id'

    project_id = fields.Many2one(
        'res.project', 'Project', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'project_id')

# ---------- Activity / Activity Group -------------


class MonitorProjectView(object):
    _name = 'monitor.project.view'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR Committed Amount',
        readonly=True,
        compute='_amount_all',
    )
    amount_po_commit = fields.Float(
        string='PO Committed Amount',
        readonly=True,
        compute='_amount_all',
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
            select min(abl.id) id, abl.project_id,
            ap.fiscalyear_id, abl.%s,
            coalesce(sum(planned_amount), 0.0) amount_plan
        from account_period ap
            join account_budget_line abl on ap.id = abl.period_id
            join account_budget ab on ab.id = abl.budget_id
        where ab.latest_version = true and ab.state in ('validate', 'done')
            and abl.%s is not null
            and abl.project_id is not null
        group by ap.fiscalyear_id, abl.project_id, abl.%s)
    """

    def _create_monitor_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field, field))

    def _prepare_pr_commit_amount_sql(self):
        """ Commit amount will invoice purchase_request """
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - purchased_qty)) amount_commit
        from purchase_request_line line
            join purchase_request doc on line.request_id = doc.id
                and (doc.date_approved is not null
                    and doc.state in ('approved'))
            join account_fiscalyear af
                on (doc.date_approved <= af.date_stop
                    and doc.date_approved >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = doc.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = doc.currency_id)
              AND ((doc.date_approved IS NOT NULL
                      AND cr2.name <= doc.date_approved)
            OR (doc.date_approved IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where line.%s = %s and af.id = %s
            and line.project_id = %s
        """
        return sql

    def _prepare_po_commit_amount_sql(self):
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - invoiced_qty)) amount_commit
        from purchase_order_line line
            join purchase_order doc on line.order_id = doc.id
                and (doc.date_approve is not null
                    and doc.state in ('approved'))
            join account_fiscalyear af
                on (doc.date_approve <= af.date_stop
                    and doc.date_approve >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = doc.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = doc.currency_id)
              AND ((doc.date_approve IS NOT NULL
                      AND cr2.name <= doc.date_approve)
            OR (doc.date_approve IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where line.%s = %s and af.id = %s
            and line.project_id = %s
        """
        return sql

    def _prepare_actual_amount_sql(self):
        sql = """
        select sum(debit-credit) amount_actual
        from account_move_line aml
            join account_period ap on ap.id = aml.period_id
        where aml.%s = %s and ap.fiscalyear_id = %s
            and aml.project_id = %s
            and journal_id in (select id from account_journal
            where type in ('purchase', 'purchase_refund'));
        """
        return sql

    @api.model
    def _get_amount_pr_commit(self):
        self._cr.execute(self._prepare_pr_commit_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.project_id.id or 0))  # Project
        return self._cr.fetchone()[0] or 0.0

    @api.model
    def _get_amount_po_commit(self):
        self._cr.execute(self._prepare_po_commit_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.project_id.id or 0))  # Project
        return self._cr.fetchone()[0] or 0.0

    @api.model
    def _get_amount_actual(self):
        self._cr.execute(self._prepare_actual_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.project_id.id or 0))  # Project
        return self._cr.fetchone()[0] or 0.0

    @api.multi
    def _amount_all(self):
        """ Overwrite, adding amount_commit """
        for rec in self:
            rec.amount_pr_commit = rec._get_amount_pr_commit()
            rec.amount_po_commit = rec._get_amount_po_commit()
            rec.amount_actual = rec._get_amount_actual()
            # Balance
            rec.amount_balance = (rec.amount_plan -
                                  (rec.amount_pr_commit +
                                   rec.amount_po_commit) -
                                  rec.amount_actual)


class AccountActivityGroupMonitorView(MonitorProjectView, models.Model):
    _name = 'account.activity.group.monitor.view'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    _budget_level = 'activity_group_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_group_id')


class AccountActivityMonitorView(MonitorProjectView, models.Model):
    _name = 'account.activity.monitor.view'
    _auto = False

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    _budget_level = 'activity_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_id')


class MonitorUnitView(object):
    _name = 'monitor.unit.view'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR Committed Amount',
        readonly=True,
        compute='_amount_all',
    )
    amount_po_commit = fields.Float(
        string='PO Committed Amount',
        readonly=True,
        compute='_amount_all',
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
            select min(abl.id) id, abl.costcenter_id,
            ap.fiscalyear_id, abl.%s,
            coalesce(sum(planned_amount), 0.0) amount_plan
        from account_period ap
            join account_budget_line abl on ap.id = abl.period_id
            join account_budget ab on ab.id = abl.budget_id
        where ab.latest_version = true and ab.state in ('validate', 'done')
            and abl.%s is not null
            and abl.costcenter_id is not null
        group by ap.fiscalyear_id, abl.costcenter_id, abl.%s)
    """

    def _create_monitor_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field, field))

    def _prepare_pr_commit_amount_sql(self):
        """ Commit amount will invoice purchase_request """
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - purchased_qty)) amount_commit
        from purchase_request_line line
            join purchase_request doc on line.request_id = doc.id
                and (doc.date_approved is not null
                    and doc.state in ('approved'))
            join account_fiscalyear af
                on (doc.date_approved <= af.date_stop
                    and doc.date_approved >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = doc.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = doc.currency_id)
              AND ((doc.date_approved IS NOT NULL
                      AND cr2.name <= doc.date_approved)
            OR (doc.date_approved IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where line.%s = %s and af.id = %s
            and line.costcenter_id = %s
        """
        return sql

    def _prepare_po_commit_amount_sql(self):
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - invoiced_qty)) amount_commit
        from purchase_order_line line
            join purchase_order doc on line.order_id = doc.id
                and (doc.date_approve is not null
                    and doc.state in ('approved'))
            join account_fiscalyear af
                on (doc.date_approve <= af.date_stop
                    and doc.date_approve >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = doc.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = doc.currency_id)
              AND ((doc.date_approve IS NOT NULL
                      AND cr2.name <= doc.date_approve)
            OR (doc.date_approve IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where line.%s = %s and af.id = %s
            and line.costcenter_id = %s
        """
        return sql

    def _prepare_actual_amount_sql(self):
        sql = """
        select sum(debit-credit) amount_actual
        from account_move_line aml
            join account_period ap on ap.id = aml.period_id
        where aml.%s = %s and ap.fiscalyear_id = %s
            and aml.costcenter_id = %s
            and journal_id in (select id from account_journal
            where type in ('purchase', 'purchase_refund'));
        """
        return sql

    @api.model
    def _get_amount_pr_commit(self):
        self._cr.execute(self._prepare_pr_commit_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.costcenter_id.id or 0))  # Costcenter
        return self._cr.fetchone()[0] or 0.0

    @api.model
    def _get_amount_po_commit(self):
        self._cr.execute(self._prepare_po_commit_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.costcenter_id.id or 0))  # Costcenter
        return self._cr.fetchone()[0] or 0.0

    @api.model
    def _get_amount_actual(self):
        self._cr.execute(self._prepare_actual_amount_sql() %
                         (self._budget_level,
                          self[self._budget_level].id,
                          self.fiscalyear_id.id,
                          self.costcenter_id.id or 0))  # Costcenter
        return self._cr.fetchone()[0] or 0.0

    @api.multi
    def _amount_all(self):
        """ Overwrite, adding amount_pr_commit """
        for rec in self:
            rec.amount_pr_commit = rec._get_amount_pr_commit()
            rec.amount_po_commit = rec._get_amount_po_commit()
            rec.amount_actual = rec._get_amount_actual()
            # Balance
            rec.amount_balance = (rec.amount_plan -
                                  (rec.amount_pr_commit +
                                   rec.amount_po_commit) -
                                  rec.amount_actual)


class AccountActivityGroupMonitorUnitView(MonitorUnitView, models.Model):
    _name = 'account.activity.group.monitor.unit.view'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    _budget_level = 'activity_group_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_group_id')


class AccountActivityMonitorUnitView(MonitorUnitView, models.Model):
    _name = 'account.activity.monitor.unit.view'
    _auto = False

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    _budget_level = 'activity_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_id')
