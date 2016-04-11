# -*- coding: utf-8 -*-
from openerp import fields, models


class ResSpa(models.Model):
    _inherit = 'res.spa'

    monitor_ids = fields.One2many(
        'res.spa.monitor.view', 'spa_id',
        string='SPA Monitor',
    )


class ResMission(models.Model):
    _inherit = 'res.mission'

    monitor_ids = fields.One2many(
        'res.mission.monitor.view', 'mission_id',
        string='Mission Monitor',
    )


class ResTagType(models.Model):
    _inherit = 'res.tag.type'

    monitor_ids = fields.One2many(
        'res.tag.type.monitor.view', 'tag_type_id',
        string='Tag Type',
    )


class ResTag(models.Model):
    _inherit = 'res.tag'

    monitor_ids = fields.One2many(
        'res.tag.monitor.view', 'tag_id',
        string='Tag',
    )


class ResMissionArea(models.Model):
    _inherit = 'res.mission.area'

    monitor_ids = fields.One2many(
        'res.mission.area.monitor.view', 'mission_area_id',
        string='Mission Area Monitor',
    )


class ResProgramGroup(models.Model):
    _inherit = 'res.program.group'

    monitor_ids = fields.One2many(
        'res.program.group.monitor.view', 'program_group_id',
        string='Program Group Monitor',
    )


class ResProgram(models.Model):
    _inherit = 'res.program'

    monitor_ids = fields.One2many(
        'res.program.monitor.view', 'program_id',
        string='Program Monitor',
    )


class ResProjectGroup(models.Model):
    _inherit = 'res.project.group'

    monitor_ids = fields.One2many(
        'res.project.group.monitor.view', 'project_group_id',
        string='Project Group Monitor',
    )


class ResProject(models.Model):
    _inherit = 'res.project'

    monitor_ids = fields.One2many(
        'res.project.monitor.view', 'project_id',
        string='Project Monitor',
    )
