# -*- coding: utf-8 -*-
import datetime
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    ChartField, CHART_VIEW, CHART_FIELDS
from openerp.addons.pabi_account_move_document_ref.models.account_move import \
    DOCTYPE_SELECT
from .common import SearchCommon, REPORT_TYPES, REPORT_GROUPBY

SEARCH_KEYS = dict(CHART_FIELDS).keys() + ['fiscalyear_id']
ALL_SEARCH_KEYS = SEARCH_KEYS + ['chart_view', 'charge_type',
                                 'activity_group_id', 'activity_id']
CHART_VIEWS = CHART_VIEW.keys()


def get_field_value(record, field):
    """ For many2one, return id, otherwise raw value """
    try:
        value = record[field] and record[field].id or False
        return value
    except Exception:
        return record[field]


def prepare_where_dict(record, keys):
    """ Based on ALL_SEARCH_KEYS, prepare where_dict """
    where_dict = {}
    for k in keys:
        value = get_field_value(record, k)
        if value:
            where_dict.update({k: value})
    return where_dict


def prepare_where_str(where):
    """
    I.e., where = {'org_id': 1, 'chart_view': 'unit_base'}
    where_clause = "org_id = 1, charg_view = 'unit_base'"
    """
    extra_where = []
    for k in where.keys():
        if where.get(k):
            if isinstance(where[k], basestring):
                extra_where.append("and %s = '%s'" % (k, where[k]))
            else:
                extra_where.append("and %s = %s" % (k, where[k]))
    where_clause = ' '.join(extra_where)
    return where_clause


class BudgetDrilldownReport(SearchCommon, models.Model):
    _name = 'budget.drilldown.report'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    line_ids = fields.One2many(
        'budget.drilldown.report.line',
        'report_id',
        string='Details'
    )
    line_internal_ids = fields.One2many(
        'budget.drilldown.report.line',
        'report_id',
        domain=[('charge_type', '=', 'internal')],
        string='Details (Internal)',
    )
    line_external_ids = fields.One2many(
        'budget.drilldown.report.line',
        'report_id',
        domain=[('charge_type', '=', 'external')],
        string='Details (External)',
    )
    line_all_ids = fields.One2many(
        'budget.drilldown.report.line',
        'report_id',
        domain=[('charge_type', '=', False)],
        string='Details'
    )

    @api.model
    def _get_report_sql(self, fields_str, where_str):
        select = ''
        group_by = ''
        if len(fields_str) > 1:
            select = '%s,' % fields_str
            group_by = 'group by %s' % fields_str
        return """
            select %s
                sum(planned_amount) planned_amount,
                sum(released_amount) released_amount,
                sum(amount_so_commit) amount_so_commit,
                sum(amount_pr_commit) amount_pr_commit,
                sum(amount_po_commit) amount_po_commit,
                sum(amount_exp_commit) amount_exp_commit,
                sum(amount_so_commit) + sum(amount_pr_commit) +
                sum(amount_po_commit) + sum(amount_exp_commit)
                    as amount_total_commit,
                sum(amount_actual) amount_actual,
                sum(amount_consumed) amount_consumed,
                sum(amount_balance) amount_balance
            from budget_monitor_report
            where budget_method = 'expense'
            %s -- more where clause
            %s -- group by
        """ % (select, where_str, group_by)

    @api.multi
    def _run_overall_report(self):
        self.ensure_one()
        # First, declare view for this report
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_overall_report_form'
        where_data = []
        # Combination of chart_view and chart_type
        for chart_view in CHART_VIEWS:
            # For internal and external
            for charge_type in ('internal', 'external'):
                where = {'chart_view': chart_view,
                         'charge_type': charge_type}
                where.update(prepare_where_dict(self, SEARCH_KEYS))
                where_data.append(where)
            # For internal + external (no charge_type)
            where = {'chart_view': chart_view}
            where.update(prepare_where_dict(self, SEARCH_KEYS))
            where_data.append(where)
        # Preparing report_lines
        report_lines = []
        for where in where_data:
            where_str = prepare_where_str(where)
            fields_str = ', '.join(where.keys())
            sql = self._get_report_sql(fields_str, where_str)
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            row = res and res[0] or where  # if res no row use where
            report_lines.append((0, 0, row))
        # --------------------------------------------------
        # For Overview Report, we need to get Rolling Amount
        # --------------------------------------------------
        Budget = self.env['account.budget']
        for report_line in report_lines:
            line = report_line[2]
            search_keys = []
            for key in line.keys():
                if key in Budget and key not in ['released_amount']:
                    search_keys.append(key)
            domain = []
            for key in search_keys:
                domain.append((key, '=', line[key]))
            consume_dom = []
            if line.get('charge_type', False):
                consume_dom = [('charge_type', '=', line['charge_type'])]
            consume_dict = dict([(x[0], x[2]) for x in consume_dom + domain])
            consume_where_str = prepare_where_str(consume_dict)
            sql = """
                select coalesce(sum(amount_actual), 0.0) actual
                from budget_consume_report
                where budget_method = 'expense'
                %s
            """ % consume_where_str
            self._cr.execute(sql)
            amount_actual = self._cr.fetchone()[0]
            # consumes = Consume.search(domain + consume_dom)
            budgets = Budget.search(domain)
            rolling = 0.0
            policy = 0.0
            # amount_actual = sum(consumes.mapped('amount_actual'))
            amount_future = 0.0
            if line.get('charge_type', False):
                if line['charge_type'] == 'internal':
                    amount_future += budgets._get_future_plan_amount_internal()
                elif line['charge_type'] == 'external':
                    amount_future += budgets._get_future_plan_amount()
                    policy = sum([x.policy_amount for x in budgets])
            else:
                amount_future += budgets._get_future_plan_amount_internal()
                amount_future += budgets._get_future_plan_amount()
                policy = sum([x.policy_amount for x in budgets])
            # Rolling
            rolling = amount_actual + amount_future
            line.update({'rolling_amount': rolling,
                         'policy_amount': policy,
                         })
        view = self.env.ref(view_xml_id)
        return (report_lines, view.id)

    @api.multi
    def _prepare_report_by_structure(self, chart_view, view_xml_id):
        self.ensure_one()
        report_lines = []
        # Prepare where and group by clause
        where = prepare_where_dict(self, ALL_SEARCH_KEYS)
        where.update({'chart_view': chart_view})
        group_by = []
        for field in REPORT_GROUPBY.get(self.report_type, []):
            groupby_field = 'group_by_%s' % field
            if self[groupby_field]:
                group_by.append(field)
        # --
        where_str = prepare_where_str(where)
        fields_str = ', '.join(group_by)
        sql = self._get_report_sql(fields_str, where_str)
        self._cr.execute(sql)
        rows = self._cr.dictfetchall()
        for row in rows:
            # Merge activity_id, activity_rpt_id => activity_id
            if row.get('activity_rpt_id', False):
                row['activity_id'] = row['activity_rpt_id']
                del row['activity_rpt_id']
            report_lines.append((0, 0, row))
        view = self.env.ref(view_xml_id)
        return (report_lines, view.id)

    @api.multi
    def _run_unit_base_report(self):
        self.ensure_one()
        chart_view = 'unit_base'
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_unit_base_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

    @api.multi
    def _run_project_base_report(self):
        self.ensure_one()
        chart_view = 'project_base'
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_project_base_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

    @api.multi
    def _run_invest_asset_base_report(self):
        self.ensure_one()
        chart_view = 'invest_asset'
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_invest_asset_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

    @api.multi
    def _run_invest_construction_report(self):
        self.ensure_one()
        chart_view = 'invest_construction'
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_invest_construction_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

    @api.model
    def generate_report(self, wizard):
        # Delete old reports run by the same user
        self.search(
            [('create_uid', '=', self.env.user.id),
             ('create_date', '<', fields.Date.context_today(self))]).unlink()
        # Create report
        RPT = dict(REPORT_TYPES)
        name = _('Budget Overview Report - %s') % RPT[wizard.report_type]
        # Fill provided search values to report head (used to execute report)
        report_dict = {'name': name}
        groupby_fields = []
        for field_list in REPORT_GROUPBY.values():
            for field in field_list:
                groupby_fields.append('group_by_%s' % field)
        groupby_fields = list(set(groupby_fields))  # remove duplicates
        search_keys = ALL_SEARCH_KEYS + groupby_fields + ['report_type']
        report_dict.update(prepare_where_dict(wizard, search_keys))
        report = self.create(report_dict)
        # Compute report lines, by report type
        report_lines = []
        view_id = False
        if report.report_type == 'overall':
            report_lines, view_id = report._run_overall_report()
        elif report.report_type == 'unit_base':
            report_lines, view_id = report._run_unit_base_report()
        elif report.report_type == 'project_base':
            report_lines, view_id = report._run_project_base_report()
        elif report.report_type == 'invest_asset':
            report_lines, view_id = report._run_invest_asset_base_report()
        elif report.report_type == 'invest_construction':
            report_lines, view_id = report._run_invest_construction_report()
        else:
            raise ValidationError(_('Selected report type is not valid!'))
        report.write({'line_ids': report_lines})
        return (report.id, view_id)

    @api.model
    def vacumm_old_reports(self):
        """ Vacumm report older than 1 day """
        old_date = datetime.datetime.now() - datetime.timedelta(days=1)
        reports = self.search([('create_date', '<',
                                old_date.strftime('%Y-%m-%d'))])
        reports.unlink()


class BudgetDrilldownReportLine(ChartField, models.Model):
    _name = 'budget.drilldown.report.line'

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        readonly=True,
    )
    report_id = fields.Many2one(
        'budget.drilldown.report',
        string='Report',
        index=True,
        ondelete='cascade',
    )
    # name = fields.Char(
    #     string='Name',
    #     compute='_compute_name',
    #     store=True,
    #     readonly=True,
    # )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Budget Plan',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Budget Policy',
        readonly=True,
    )
    rolling_amount = fields.Float(
        string='Rolling Plan',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Budget Release',
        readonly=True,
    )
    amount_so_commit = fields.Float(
        string='SO Commitment',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR Commit',
        readonly=True,
    )
    amount_po_commit = fields.Float(
        string='PO Commit',
        readonly=True,
    )
    amount_exp_commit = fields.Float(
        string='Expense Commit',
        readonly=True,
    )
    amount_total_commit = fields.Float(
        string='Total Commit',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual',
        readonly=True,
    )
    amount_consumed = fields.Float(
        string='Total Spent',
        readonly=True,
    )
    amount_balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    product_activity_id = fields.Many2one(
        'product.activity',
        string='Product/Activity',
        readonly=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    quarter = fields.Selection(
        [('Q1', 'Q1'),
         ('Q2', 'Q2'),
         ('Q3', 'Q3'),
         ('Q4', 'Q4'),
         ],
        string='Quarter',
        readonly=True,
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        readonly=True,
        help="Reference to original document",
    )
    document_line = fields.Char(
        string='Document Line',
        readonly=True,
        help="Reference to original document line",
    )
    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity Rpt',
        readonly=True,
    )

    # @api.multi
    # def _compute_name(self):
    #     """ Concat dimension all dimension in a valid order """
    #     fields_order = (
    #         'org_id', 'division_id', 'section_id',
    #         'project_id', 'invest_asset_id', 'invest_construction_id',
    #         'activity_group_id', 'activity_id')
    #     for rec in self:
    #         names = []
    #         for f in fields_order:
    #             if f in rec:
    #                 if len(rec[f]) == 0:
    #                     continue
    #                 if 'display_name' in rec[f]:
    #                     names.append(str(rec[f].display_name))
    #                 else:
    #                     names.append(str(rec[f]))
    #         rec.name = ' / '.join(names)

    @api.multi
    def open_so_commit_items(self):
        return self.open_items('so_commit')

    @api.multi
    def open_pr_commit_items(self):
        return self.open_items('pr_commit')

    @api.multi
    def open_po_commit_items(self):
        return self.open_items('po_commit')

    @api.multi
    def open_exp_commit_items(self):
        return self.open_items('exp_commit')

    @api.multi
    def open_total_commit_items(self):
        return self.open_items('total_commit')

    @api.multi
    def open_actual_items(self):
        return self.open_items('actual')

    @api.multi
    def open_consumed_items(self):
        return self.open_items()

    @api.multi
    def open_items(self, ttype=False):
        self.ensure_one()
        where_dict = prepare_where_dict(self, ALL_SEARCH_KEYS)
        if ttype and ttype not in ('total_commit'):
            where_dict.update({'budget_commit_type': ttype})
        where_str = prepare_where_str(where_dict)
        # Special Where
        if ttype == 'total_commit':
            where_str += " and budget_commit_type in" \
                         " ('so_commit', 'pr_commit'," \
                         " 'po_commit', 'exp_commit')"
        sql = """
            select analytic_line_id
            from budget_monitor_report
            where budget_method = 'expense'
            %s
        """ % where_str
        self._cr.execute(sql)
        res = self._cr.fetchall()
        analytic_line_ids = [x[0] for x in res]
        return {
            'name': _("Analytic Lines"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', analytic_line_ids)],
        }
