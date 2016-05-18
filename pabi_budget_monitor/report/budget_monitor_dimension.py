# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools


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
