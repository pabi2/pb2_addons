# -*- coding: utf-8 -*-
from openerp import fields, models


# ------------------ Activity ------------------
class AccountActivityGroupMonitorView(models.Model):
    _inherit = 'account.activity.group.monitor.view'


class AccountActivityMonitorView(models.Model):
    _inherit = 'account.activity.monitor.view'


# ------------------ Unit Based ------------------
class ResOrgMonitorView(models.Model):
    _name = 'res.org.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'org_id'

    org_id = fields.Many2one(
        'res.org', 'Org', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResSectorMonitorView(models.Model):
    _name = 'res.sector.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'sector_id'

    sector_id = fields.Many2one(
        'res.sector', 'Sector', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResSubsectorMonitorView(models.Model):
    _name = 'res.subsector.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'subsector_id'

    subsector_id = fields.Many2one(
        'res.subsector', 'Subsector', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResDivisionMonitorView(models.Model):
    _name = 'res.division.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'division_id'

    division_id = fields.Many2one(
        'res.division', 'Division', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResSectionMonitorView(models.Model):
    _name = 'res.section.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'section_id'

    section_id = fields.Many2one(
        'res.section', 'Section', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResCostcenterMonitorView(models.Model):
    _name = 'res.costcenter.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'costcenter_id'

    costcenter_id = fields.Many2one(
        'res.costcenter', 'Costcenter', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ------------------ Tags ------------------
class ResSpaMonitorView(models.Model):
    _name = 'res.spa.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'spa_id'

    spa_id = fields.Many2one(
        'res.spa', 'SPA', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResMissionMonitorView(models.Model):
    _name = 'res.mission.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'mission_id'

    mission_id = fields.Many2one(
        'res.mission', 'Mission', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResTagTypeMonitorView(models.Model):
    _name = 'res.tag.type.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'tag_type_id'

    tag_type_id = fields.Many2one(
        'res.tag.type', 'Tag Type', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResTagMonitorView(models.Model):
    _name = 'res.tag.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'tag_id'

    tag_id = fields.Many2one(
        'res.tag', 'Tag', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ------------------ Project Based ------------------
class ResFunctionalAreaMonitorView(models.Model):
    _name = 'res.functional.area.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'functional_area_id'

    functional_area_id = fields.Many2one(
        'res.functional.area', 'Functional Area', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResProgramGroupMonitorView(models.Model):
    _name = 'res.program.group.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'program_group_id'

    program_group_id = fields.Many2one(
        'res.program.group', 'Program Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResProgramMonitorView(models.Model):
    _name = 'res.program.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'program_id'

    program_id = fields.Many2one(
        'res.program', 'Program', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResProjectGroupMonitorView(models.Model):
    _name = 'res.project.group.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'project_group_id'

    project_group_id = fields.Many2one(
        'res.project.group', 'Project Group', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResProjectMonitorView(models.Model):
    _name = 'res.project.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'project_id'

    project_id = fields.Many2one(
        'res.project', 'Project', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ----------------- Personnel --------------------
class ResPersonnelCostcenterMonitorView(models.Model):
    _name = 'res.personnel.costcenter.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'personnel_costcenter_id'

    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter', 'Personnel Budget', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ----------------- Investment --------------------
class ResInvestAssetMonitorView(models.Model):
    _name = 'res.invest.asset.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'invest_asset_id'

    invest_asset_id = fields.Many2one(
        'res.invest.asset', 'Investment Asset', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResInvestConstructionMonitorView(models.Model):
    _name = 'res.invest.construction.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'invest_construction_id'

    invest_construction_id = fields.Many2one(
        'res.invest.construction', 'Investment Construction', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResInvestConstructionPhaseMonitorView(models.Model):
    _name = 'res.invest.construction.phase.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'invest_construction_phase_id'

    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        'Investment Construction Phase', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ------------------ Job Order ------------------
class ResCostControlMonitorView(models.Model):
    _name = 'res.cost.control.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'cost_control_id'

    cost_control_id = fields.Many2one(
        'cost.control', 'Job Order', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResCostControlTypeMonitorView(models.Model):
    _name = 'res.cost.control.type.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'cost_control_type_id'

    cost_control_type_id = fields.Many2one(
        'cost.control', 'Job Order Type', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


# ---------------------- Fund ---------------------
class ResFundMonitorProjectView(models.Model):
    _name = 'res.fund.monitor.project.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'fund_id, project_id'

    fund_id = fields.Many2one(
        'res.fund', 'Fund', readonly=True)
    project_id = fields.Many2one(
        'res.project', 'Project', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResFundMonitorSectionView(models.Model):
    _name = 'res.fund.monitor.section.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'fund_id, section_id'

    fund_id = fields.Many2one(
        'res.fund', 'Fund', readonly=True)
    section_id = fields.Many2one(
        'res.section', 'Section', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResFundMonitorInvestAssetView(models.Model):
    _name = 'res.fund.monitor.invest.asset.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'fund_id, invest_asset_id'

    fund_id = fields.Many2one(
        'res.fund', 'Fund', readonly=True)
    invest_asset_id = fields.Many2one(
        'res.invest.asset', 'Invest Asset', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResFundMonitorInvestConstructionPhaseView(models.Model):
    _name = 'res.fund.monitor.invest.construction.phase.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'fund_id, invest_construction_phase_id'

    fund_id = fields.Many2one(
        'res.fund', 'Fund', readonly=True)
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        'Invest Construction Phase', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class ResFundMonitorPersonnelCostcenterView(models.Model):
    _name = 'res.fund.monitor.personnel.costcenter.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'fund_id, personnel_costcenter_id'

    fund_id = fields.Many2one(
        'res.fund', 'Fund', readonly=True)
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter', 'Personnel Costcenter', readonly=True)

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)
