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


class ResDivisionGroup(models.Model):
    _inherit = 'res.division.group'

    monitor_ids = fields.One2many(
        'res.division.group.monitor.view', 'division_group_id',
        string='Division Group Monitor',
    )


class ResDivision(models.Model):
    _inherit = 'res.division'

    monitor_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
    )


class ResDepartment(models.Model):
    _inherit = 'res.department'

    monitor_ids = fields.One2many(
        'res.department.monitor.view', 'department_id',
        string='Department Monitor',
    )


class ResCostcenter(models.Model):
    _inherit = 'res.costcenter'

    monitor_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
    )
