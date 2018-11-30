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
    def _get_report_sql(self, fields_str, where_str, budget_method='expense'):
        select = ''
        group_by = ''
        if len(fields_str) > 1:
            select = '%s,' % fields_str
            group_by = 'group by %s' % fields_str
        return """
            select %s
                coalesce(sum(planned_amount), 0.0) planned_amount,
                coalesce(sum(released_amount), 0.0) released_amount,
                coalesce(sum(amount_so_commit), 0.0) amount_so_commit,
                coalesce(sum(amount_pr_commit), 0.0) amount_pr_commit,
                coalesce(sum(amount_po_commit), 0.0) amount_po_commit,
                coalesce(sum(amount_exp_commit), 0.0) amount_exp_commit,
                coalesce(sum(amount_so_commit), 0.0) +
                coalesce(sum(amount_pr_commit), 0.0) +
                coalesce(sum(amount_po_commit), 0.0) +
                coalesce(sum(amount_exp_commit), 0.0) as amount_total_commit,
                sum(amount_actual) amount_actual,
                sum(amount_consumed) amount_consumed,
                sum(amount_balance) amount_balance
            from budget_monitor_report
            where budget_method = '%s'
            %s -- more where clause
            %s -- group by
        """ % (select, budget_method, where_str, group_by)

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
            sql = self._get_report_sql(fields_str, where_str)  # Expense
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
        rows = self._query_report_by_structure(chart_view)
        for row in rows:
            # Merge activity_id, activity_rpt_id => activity_id
            if row.get('activity_rpt_id', False):
                row['activity_id'] = row['activity_rpt_id']
                del row['activity_rpt_id']
            row['chartfield_ids'] = [(6, 0, self.chartfield_ids.ids)]
            if self._context.get('action_type', False) == 'my_budget_report':
                if self.report_type == 'unit_base':
                    section_ids = self._get_domain_section()[0][2]
                    if self.section_ids:
                        section_ids = self.section_ids.ids
                    row['section_ids'] = [(6, 0, section_ids)]
                if self.report_type == 'project_base':
                    project_ids = self._get_domain_project()[0][2]
                    if self.project_ids:
                        project_ids = self.project_ids.ids
                    row['project_ids'] = [(6, 0, project_ids)]
            report_lines.append((0, 0, row))
        view = self.env.ref(view_xml_id)
        return (report_lines, view.id)

    @api.multi
    def _update_where_str(self, where_str, fields_str):
        # Chartfield
        if self.chartfield_id.model == 'res.section':
            where_str += ' and section_id = %s' % self.chartfield_id.res_id
        if self.chartfield_id.model == 'res.project':
            where_str += ' and project_id = %s' % self.chartfield_id.res_id
        if self.chartfield_id.model == 'res.invest.construction.phase':
            where_str += ' and invest_construction_phase_id = %s' % \
                self.chartfield_id.res_id
        if self.chartfield_id.model == 'res.invest.asset':
            where_str += ' and invest_asset_id = %s' % \
                self.chartfield_id.res_id
        if self.chartfield_id.model == 'res.personnel.costcenter':
            where_str += ' and personnel_costcenter_id = %s' % \
                self.chartfield_id.res_id

        section_ids = \
            self.chartfield_ids.filtered(lambda x: x.model == 'res.section') \
            .mapped('res_id')
        project_ids = \
            self.chartfield_ids.filtered(lambda x: x.model == 'res.project') \
            .mapped('res_id')
        invest_asset_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.invest.asset').mapped('res_id')
        personnel_costcenter_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.personnel.costcenter') \
            .mapped('res_id')
        invest_construction_phase_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.invest.construction.phase') \
            .mapped('res_id')

        where_list = []
        if section_ids:
            where_list.append(
                'section_id in %s' % str(tuple(section_ids + [0])))
        if project_ids:
            where_list.append(
                'project_id in %s' % str(tuple(project_ids + [0])))
        if invest_asset_ids:
            where_list.append(
                'invest_asset_id in %s' % str(tuple(invest_asset_ids + [0])))
        if personnel_costcenter_ids:
            where_list.append(
                'personnel_costcenter_id in %s' %
                str(tuple(personnel_costcenter_ids + [0])))
        if invest_construction_phase_ids:
            where_list.append(
                'invest_construction_phase_id in %s' %
                str(tuple(invest_construction_phase_ids + [0])))
        if where_list:
            where_str += ' and (' + ' or '.join(where_list) + ')'
        if self['group_by_chartfield_id']:
            group_chartfield = 'section_id, project_id, invest_asset_id, \
                                personnel_costcenter_id, \
                                invest_construction_phase_id'
            fields_str += fields_str and ', %s' % group_chartfield or \
                group_chartfield
        # For my budget report
        if self._context.get('action_type', False) == 'my_budget_report':
            if self.report_type == 'unit_base':
                section_ids = self._get_domain_section()[0][2]
                if self.section_ids:
                    section_ids = self.section_ids.ids
                where_str += ' and section_id in %s' % \
                    str(tuple(section_ids + [0, 0]))
            if self.report_type == 'project_base':
                project_ids = self._get_domain_project()[0][2]
                if self.project_ids:
                    project_ids = self.project_ids.ids
                where_str += ' and project_id in %s' % \
                    str(tuple(project_ids + [0, 0]))
        return where_str, fields_str

    @api.multi
    def _query_report_by_structure(self, chart_view, budget_method='expense'):
        self.ensure_one()
        where = prepare_where_dict(self, ALL_SEARCH_KEYS)
        if chart_view:
            where.update({'chart_view': chart_view})

        group_by = []
        for field in REPORT_GROUPBY.get(self.report_type, []):
            groupby_field = 'group_by_%s' % field
            if self[groupby_field]:
                group_by.append(field)

        # if chart_view == 'invest_construction':
        #     group_by.append('invest_construction_phase_id')

        # --
        where_str = prepare_where_str(where)
        fields_str = ', '.join(group_by)

        # update where_str and field_str
        where_str, fields_str = self._update_where_str(
            where_str, fields_str)

        # SQL
        sql = self._get_report_sql(fields_str, where_str, budget_method)
        self._cr.execute(sql)
        rows = self._cr.dictfetchall()
        return rows

    @api.multi
    def _run_all_report(self):
        self.ensure_one()
        chart_view = False
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_all_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

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

    @api.multi
    def _run_personnel_report(self):
        self.ensure_one()
        chart_view = 'personnel'
        view_xml_id = 'pabi_budget_drilldown_report.' \
                      'view_budget_personnel_report_form'
        return self._prepare_report_by_structure(chart_view, view_xml_id)

    @api.model
    def generate_report(self, wizard):
        # Delete old reports run by the same user
        self.search(
            [('create_uid', '=', self.env.user.id),
             ('create_date', '<', fields.Date.context_today(self))]).unlink()
        # Create report
        RPT = dict(REPORT_TYPES)
        title = 'Budget Overview Report'
        # My budget report
        if self._context.get('action_type', False) == 'my_budget_report':
            title = 'My Budget Report'

        name = _('%s - %s') % (title, RPT[wizard.report_type])
        # Fill provided search values to report head (used to execute report)
        report_dict = {'name': name}
        groupby_fields = []

        # If report type = all
        groupby_chartfield = [[]]
        if wizard.report_type == 'all':
            groupby_chartfield[0].append('chartfield_id')

        for field_list in REPORT_GROUPBY.values() + groupby_chartfield:
            for field in field_list:
                groupby_fields.append('group_by_%s' % field)
        groupby_fields = list(set(groupby_fields))  # remove duplicates
        search_keys = ALL_SEARCH_KEYS + groupby_fields + ['report_type']

        # update search keys
        search_keys.extend(['chartfield_id', 'action_type'])

        report_dict.update(prepare_where_dict(wizard, search_keys))

        # Write many2many field
        if wizard.section_ids:
            report_dict.update({'section_ids':
                                [(6, 0, wizard.section_ids.ids)]})
        if wizard.project_ids:
            report_dict.update({'project_ids':
                                [(6, 0, wizard.project_ids.ids)]})
        if wizard.chartfield_ids:
            report_dict.update({'chartfield_ids':
                                [(6, 0, wizard.chartfield_ids.ids)]})
        report = self.create(report_dict)

        # Compute report lines, by report type
        report_lines = []
        view_id = False
        if report.report_type == 'all':
            report_lines, view_id = report._run_all_report()
        elif report.report_type == 'overall':
            report_lines, view_id = report._run_overall_report()
        elif report.report_type == 'unit_base':
            report_lines, view_id = report._run_unit_base_report()
        elif report.report_type == 'project_base':
            report_lines, view_id = report._run_project_base_report()
        elif report.report_type == 'invest_asset':
            report_lines, view_id = report._run_invest_asset_base_report()
        elif report.report_type == 'invest_construction':
            report_lines, view_id = report._run_invest_construction_report()
        elif report.report_type == 'personnel':
            report_lines, view_id = report._run_personnel_report()
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

    # A web service method, return result as list of dictionary
    @api.model
    def get_project_budget_summary(self, fiscalyear, project_name,
                                   budget_method, charge_type=False,
                                   extra_project_fields={}):
        """ This method query and return result as dictionary
        required params: fiscalyear, project_name,
                         budget_method (expense/revenus)
        params: charge_type (internal/external) - if not specified, run both.
                extra_project_fields - as list of more fields to show
        return: [{
            'fiscalyear': '2018',
            'code': 'P1001', 'name': 'Project XYZ', 'state': 'approve',
            # Budget Related Fields
            'planned_amount': 50000.0,
            'released_amount': 4939149.54,
            'amount_so_commit': 0.0,
            'amount_pr_commit': 0.0,
            'amount_po_commit': 4507000.0,
            'amount_exp_commit': 0.0,
            'amount_total_commit': 4507000.0,
            'amount_actual': 332149.54,
            'amount_consumed': 4839149.54,
            'amount_balance': 100000.00,
            # More Data from extra_project_fields, i.e.,
            ...
            ...
            }]
        """
        # Prepare search criteria
        if budget_method not in ('expense', 'revenue'):
            raise ValidationError(
                _('Budget Method is not specified (expense/revenue)'))
        Fiscalyear = self.env['account.fiscalyear']
        Project = self.env['res.project']
        fiscalyear_id = Fiscalyear.name_search(fiscalyear, operator='=')
        if len(fiscalyear_id) != 1:
            raise ValidationError(_('Fiscalyear %s not found') % fiscalyear)
        project_id = Project.name_search(project_name, operator='=')
        if len(project_id) != 1:
            raise ValidationError(_('Project %s not found') % project_name)
        chart_view = 'project_base'
        # Create report, with search criteria / group by
        fiscalyear = Fiscalyear.browse(fiscalyear_id[0][0])
        project = Project.browse(project_id[0][0])
        report = self.create({'name': chart_view,  # won't be used anywhere
                              'report_type': chart_view,
                              'charge_type': charge_type,
                              'company_id': self.env.user.company_id.id,
                              # Serach criteria
                              'fiscalyear_id': fiscalyear.id,
                              'project_id': project.id,
                              })
        result = report._query_report_by_structure(chart_view, budget_method)
        # Basic info
        result[0]['fiscalyear'] = fiscalyear.name
        result[0]['project_code'] = project.code
        result[0]['project'] = project.name
        result[0]['state'] = project.state
        # More project information
        extra_project_fields = {
            'project_group': 'project_group_id.display_name',
            'program': 'program_id.display_name',
            'ref_program': 'ref_program_id.display_name',
            'proposal_program': 'proposal_program_id.display_name',
            'program_group': 'program_group_id.display_name',
            'functional_area': 'functional_area_id.display_name',
            'require_fund_rule': 'require_fund_rule',
            'pm_employee': 'pm_employee_id.display_name',
            'analyst_employee': 'analyst_employee_id.display_name',
            'external_pm': 'external_pm',
            'costcenter': 'costcenter_id.display_name',
            'org': 'org_id.display_name',
            'date_start': 'date_start',
            'date_approve': 'date_approve',
            'date_end': 'date_end',
            'project_date_start': 'project_date_start',
            'project_ddate_end': 'project_date_end',
            'contract_date_start': 'contract_date_start',
            'contract_date_end': 'contract_date_end',
            'project_date_end_proposal': 'project_date_end_proposal',
            'project_date_close_cond': 'project_date_close_cond',
            'project_date_close': 'project_date_close',
            'project_date_terminate': 'project_date_terminate',
            'project_status': 'project_status.display_name',
            'mission': 'mission_id.display_name',
            'project_type': 'project_type_id.display_name',
            'fund_type': 'fund_type_id.display_name',
            'operation': 'operation_id.display_name',
            'master_plan': 'master_plan_id.display_name',
            'subprogram': 'subprogram_id.display_name',
            'nstda_strategy': 'nstda_strategy_id.display_name',
            'target_program': 'target_program_id.display_name',
        }.update(extra_project_fields)  # If there are more
        for key, field in extra_project_fields.iteritems():
            result[0][key] = self._get_field_data(field, project)
        return result

    @api.model
    def get_project_budget_detail(self, fiscalyear, project_name,
                                  budget_method, charge_type=False):
        Analytic = self.env['account.analytic.line']
        # Prepare search criteria
        if budget_method not in ('expense', 'revenue'):
            raise ValidationError(
                _('Budget Method is not specified (expense/revenue)'))
        Fiscalyear = self.env['account.fiscalyear']
        Project = self.env['res.project']
        fiscalyear_id = Fiscalyear.name_search(fiscalyear, operator='=')
        if len(fiscalyear_id) != 1:
            raise ValidationError(_('Fiscalyear %s not found') % fiscalyear)
        project_id = Project.name_search(project_name, operator='=')
        if len(project_id) != 1:
            raise ValidationError(_('Project %s not found') % project_name)
        chart_view = 'project_base'
        # Create report, with search criteria / group by
        fiscalyear = Fiscalyear.browse(fiscalyear_id[0][0])
        project = Project.browse(project_id[0][0])
        report_line = self.env['budget.drilldown.report.line'].create({
            'chart_view': chart_view,
            'charge_type': charge_type,
            'budget_method': budget_method,
            'fiscalyear_id': fiscalyear.id,
            'project_id': project.id,
            'company_id': self.env.user.company_id.id,
        })
        ids = report_line._query_open_items(False, budget_method)
        analytics = Analytic.search([('id', 'in', list(set(ids)))])
        results = []
        for analytic in analytics:
            result = {}
            result['fiscalyear'] = fiscalyear.name
            result['period'] = analytic.period_id.name
            result['project_code'] = project.code
            result['project'] = project.name
            result['state'] = project.state
            result['document'] = analytic.document
            result['document_line'] = analytic.document_line
            result['document_date'] = analytic.document_date
            result['posting_date'] = analytic.date
            result['ref'] = analytic.ref
            result['amount'] = analytic.amount
            result['activity_group_code'] = analytic.activity_group_id.code
            result['activity_group'] = analytic.activity_group_id.name
            result['activity_code'] = analytic.activity_id.code
            result['activity'] = analytic.activity_id.name
            result['account_code'] = analytic.general_account_id.code
            result['account'] = analytic.general_account_id.name
            result['job_order_code'] = analytic.cost_control_id.code
            result['job_order'] = analytic.cost_control_id.code
            result['fund'] = analytic.fund_id.name
            result['po_contract'] = \
                analytic.purchase_id.contract_id.display_name
            result['purchase_method'] = \
                analytic.purchase_request_id.purchase_method_id.display_name
            result['partner_code'] = analytic.partner_id.search_key
            result['partner'] = analytic.partner_id.name
            result['amount'] = analytic.amount
            result['requester'] = analytic.request_emp_id.display_name
            result['preparer'] = analytic.prepare_emp_id.display_name
            result['approver'] = analytic.approve_emp_id.display_name
            result['doctype'] = analytic.doctype
            results.append(result)
        return results

    @api.model
    def _get_field_data(self, _field, _record):
        """ Get field data, and convert data type if needed, i.e.,
        _field = 'partner_id.address_id.province_id.name'
        """
        if not _field:
            return None
        line_copy = _record
        for f in _field.split('.'):
            data_type = line_copy._fields[f].type
            line_copy = line_copy[f]
            if data_type == 'date':
                if line_copy:
                    line_copy = datetime.datetime.strptime(line_copy,
                                                           '%Y-%m-%d')
            elif data_type == 'datetime':
                if line_copy:
                    line_copy = datetime.datetime.strptime(line_copy,
                                                           '%Y-%m-%d %H:%M:%S')
        if isinstance(line_copy, basestring):
            line_copy = line_copy.encode('utf-8')
        return line_copy


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
    section_ids = fields.Many2many(
        'res.section',
        string='Section',
    )
    project_ids = fields.Many2many(
        'res.project',
        string='Project',
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budgets',
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
        compute='_compute_chartfield',
        store=True,
    )

    @api.multi
    @api.depends('section_id', 'project_id', 'invest_asset_id',
                 'personnel_costcenter_id', 'invest_construction_phase_id')
    def _compute_chartfield(self):
        ChartField = self.env['chartfield.view']
        for rec in self:
            model = False
            res_id = False
            if rec.section_id:
                model = 'res.section'
                res_id = rec.section_id.id
            elif rec.project_id:
                model = 'res.project'
                res_id = rec.project_id.id
            elif rec.invest_asset_id:
                model = 'res.invest.asset'
                res_id = rec.invest_asset_id.id
            elif rec.personnel_costcenter_id:
                model = 'res.personnel.costcenter'
                res_id = rec.personnel_costcenter_id.id
            elif rec.invest_construction_phase_id:
                model = 'res.invest.construction.phase'
                res_id = rec.invest_construction_phase_id.id
            rec.chartfield_id = ChartField.search(
                [('model', '=', model), ('res_id', '=', res_id)])

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
        analytic_line_ids = self._query_open_items(ttype=ttype)
        return {
            'name': _("Analytic Lines"),
            'view_type': 'form',
            # 'view_mode': 'tree,form',
            # 'res_model': 'account.analytic.line',
            'view_mode': 'tree',
            'res_model': 'account.analytic.line.view',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', analytic_line_ids)],
        }

    @api.multi
    def _update_where_str(self, where_str):
        section_ids = \
            self.chartfield_ids.filtered(lambda x: x.model == 'res.section') \
            .mapped('res_id')
        project_ids = \
            self.chartfield_ids.filtered(lambda x: x.model == 'res.project') \
            .mapped('res_id')
        invest_asset_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.invest.asset').mapped('res_id')
        personnel_costcenter_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.personnel.costcenter') \
            .mapped('res_id')
        invest_construction_phase_ids = \
            self.chartfield_ids.filtered(
                lambda x: x.model == 'res.invest.construction.phase') \
            .mapped('res_id')

        where_list = []
        if section_ids:
            where_list.append(
                'section_id in %s' % str(tuple(section_ids + [0])))
        if project_ids:
            where_list.append(
                'project_id in %s' % str(tuple(project_ids + [0])))
        if invest_asset_ids:
            where_list.append(
                'invest_asset_id in %s' % str(tuple(invest_asset_ids + [0])))
        if personnel_costcenter_ids:
            where_list.append(
                'personnel_costcenter_id in %s' %
                str(tuple(personnel_costcenter_ids + [0])))
        if invest_construction_phase_ids:
            where_list.append(
                'invest_construction_phase_id in %s' %
                str(tuple(invest_construction_phase_ids + [0])))
        if where_list:
            where_str += ' and (' + ' or '.join(where_list) + ')'
        if self.section_ids:
            where_str += ' and section_id in %s' \
                % str(tuple(self.section_ids.ids + [0]))
        if self.project_ids:
            where_str += ' and project_id in %s' \
                % str(tuple(self.project_ids.ids + [0]))
        return where_str

    @api.multi
    def _query_open_items(self, ttype=False, budget_method='expense'):
        self.ensure_one()
        where_dict = prepare_where_dict(self, ALL_SEARCH_KEYS)
        if ttype and ttype not in ('total_commit'):
            where_dict.update({'budget_commit_type': ttype})
        fiscalyear_id = self.report_id.fiscalyear_id.id
        where_str = prepare_where_str(where_dict)

        # Update where_str
        where_str += self._update_where_str(where_str)
        # Special Where
        if ttype == 'total_commit':
            where_str += " and budget_commit_type in" \
                         " ('so_commit', 'pr_commit'," \
                         " 'po_commit', 'exp_commit')"
        sql = """
            select analytic_line_id
            from budget_monitor_report
            where fiscalyear_id = %s and budget_method = '%s'
            %s
        """ % (fiscalyear_id, budget_method, where_str)
        self._cr.execute(sql)
        res = self._cr.fetchall()
        analytic_line_ids = [x[0] for x in res]
        return analytic_line_ids
