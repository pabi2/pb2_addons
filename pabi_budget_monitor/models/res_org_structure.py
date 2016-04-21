# -*- coding: utf-8 -*-
from openerp import fields, models


class ResOrg(models.Model):
    _inherit = 'res.org'

    monitor_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
    )


class ResSector(models.Model):
    _inherit = 'res.sector'

    monitor_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
    )


class ResSubsector(models.Model):
    _inherit = 'res.subsector'

    monitor_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
    )


class ResDivision(models.Model):
    _inherit = 'res.division'

    monitor_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
    )


class ResSection(models.Model):
    _inherit = 'res.section'

    monitor_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section',
    )


class ResCostcenter(models.Model):
    _inherit = 'res.costcenter'

    monitor_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
    )
