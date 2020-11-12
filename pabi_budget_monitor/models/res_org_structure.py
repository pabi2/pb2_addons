# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResOrg(models.Model):
    _inherit = 'res.org'

    monitor_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.org.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Org Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.org.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Org Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Division Struture
        self._cr.execute("""delete from res_org_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where org_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.org.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_org(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_org_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSector(models.Model):
    _inherit = 'res.sector'

    monitor_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.sector.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Sector Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.sector.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Sector Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Division Struture
        self._cr.execute("""delete from res_sector_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where sector_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.sector.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_sector(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_sector_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSubsector(models.Model):
    _inherit = 'res.subsector'

    monitor_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.subsector.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Subsector Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.subsector.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Subsector Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Division Struture
        self._cr.execute("""delete from res_subsector_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where subsector_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.subsector.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_subsector(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_subsector_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResDivision(models.Model):
    _inherit = 'res.division'

    monitor_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.division.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Division Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.division.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Division Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Division Struture
        self._cr.execute("""delete from res_division_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where division_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.division.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_division(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_division_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSection(models.Model):
    _inherit = 'res.section'

    monitor_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        readonly=True,
    )
    job_order_ids = fields.Many2many(
        'cost.control',
        string='Job Order',
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.section.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Section Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.section.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Section Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Section Struture
        self._cr.execute("""delete from res_section_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where section_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.section.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_section(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_section_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResCostcenter(models.Model):
    _inherit = 'res.costcenter'

    monitor_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        comodel_name='res.costcenter.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Costcenter Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        comodel_name='res.costcenter.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Costcenter Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new section not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on Section Struture
        self._cr.execute("""delete from res_costcenter_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where costcenter_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.costcenter.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True

    @api.multi
    def action_open_budget_monitor_costcenter(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_costcenter_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResDivisionMonitorViewOnly(models.TransientModel):
    _name = 'res.division.monitor.only.view'
    _inherit = 'monitor.view'


class ResSectionMonitorViewOnly(models.TransientModel):
    _name = 'res.section.monitor.only.view'
    _inherit = 'monitor.view'


class ResSubSectorMonitorViewOnly(models.TransientModel):
    _name = 'res.subsector.monitor.only.view'
    _inherit = 'monitor.view'


class ResSectorMonitorViewOnly(models.TransientModel):
    _name = 'res.sector.monitor.only.view'
    _inherit = 'monitor.view'


class ResOrgMonitorViewOnly(models.TransientModel):
    _name = 'res.org.monitor.only.view'
    _inherit = 'monitor.view'


class ResCostcenterMonitorViewOnly(models.TransientModel):
    _name = 'res.costcenter.monitor.only.view'
    _inherit = 'monitor.view'
