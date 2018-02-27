# -*- coding: utf-8 -*-
from openerp import models, fields
from .res_common import ResCommon


class ProjectFundType(ResCommon, models.Model):
    _name = 'project.fund.type'


class ProjectType(ResCommon, models.Model):
    _name = 'project.type'


class ProjectOperation(ResCommon, models.Model):
    _name = 'project.operation'


class ProjectMasterPlan(ResCommon, models.Model):
    _name = 'project.master.plan'


class ProjectNSTDAStrategy(ResCommon, models.Model):
    _name = 'project.nstda.strategy'

    group_id = fields.Many2one(
        'project.nstda.strategy.group',
        string='Group',
    )


class ProjectNSTDAStrategyGroup(ResCommon, models.Model):
    _name = 'project.nstda.strategy.group'
