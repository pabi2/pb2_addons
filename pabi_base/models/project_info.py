# -*- coding: utf-8 -*-
from openerp import models, fields
from .res_common import ResCommon


class ProjectFundType(ResCommon, models.Model):
    _name = 'project.fund.type'


class ProjectType(ResCommon, models.Model):
    _name = 'project.type'

    project_kind = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non Research'),
         ('management', 'Management Program/Cluster'),
         ('construction', 'Construction'), ],
        string='Project Kind',
    )


class ProjectOperation(ResCommon, models.Model):
    _name = 'project.operation'


class ProjectObjective(ResCommon, models.Model):
    _name = 'project.objective'


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
