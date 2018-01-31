# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_base.models.res_common import ResCommon

# SPA Structure:
# --------------
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)    (type/tag)
#        (org)           (org)        (org)         (org)         (org)
# functional_area -> program_group -> program -> project_group -> project
#                                    (spa(s))                   (mission)
#                                                                (fund)


class SpaStructureTag(object):

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
        related='tag_id.tag_type_id',
        readonly=True,
        required=False,
    )
    tag_id = fields.Many2one(
        'res.tag',
        string='Tag',
        required=False,
    )


class ResSpa(models.Model):
    _name = 'res.spa'
    _description = 'SPA'

    name = fields.Char(
        string='Name',
        required=True,
    )
    begin_period_id = fields.Many2one(
        'account.period',
        string='Begin Period',
    )
    end_period_id = fields.Many2one(
        'account.period',
        string='End Period',
    )
    begin_date = fields.Date(
        string='Begin Date',
        compute='_compute_date',
        store=True,
    )
    end_date = fields.Date(
        string='End Date',
        compute='_compute_date',
        store=True,
    )

    @api.one
    @api.depends('begin_period_id', 'end_period_id')
    def _compute_date(self):
        self.begin_date = self.begin_period_id.date_start
        self.end_date = self.end_period_id.date_stop

    @api.constrains('begin_period_id', 'end_period_id')
    def _validate_period_range(self):
        if not self.begin_period_id or not self.end_period_id:
            return True
        if self.begin_date >= self.end_date:
            raise ValidationError(_('Date range error!'))
        # Duplicated range?
        overlaps1 = len(self.search([('begin_date', '<=', self.begin_date),
                                    ('end_date', '>=', self.begin_date),
                                    ('id', '!=', self.id)])._ids)
        overlaps2 = len(self.search([('begin_date', '<=', self.end_date),
                                    ('end_date', '>=', self.end_date),
                                    ('id', '!=', self.id)])._ids)
        if overlaps1 or overlaps2:
            raise ValidationError(
                _('This SPA has overlap period with other SPA!'))


class ResMission(models.Model):
    _name = 'res.mission'
    _description = 'Mission'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )


class ResTagType(models.Model):
    _name = 'res.tag.type'
    _description = 'Tag Type'

    name = fields.Char(
        string='Name',
        required=True,
    )


class ResTag(models.Model):
    _name = 'res.tag'
    _description = 'Tag'

    name = fields.Char(
        string='Name',
        required=True,
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
        required=True,
    )

    @api.multi
    def name_get(self):
        result = []
        for tag in self:
            result.append((tag.id, tag.tag_type_id.name + " / " + tag.name))
        return result


class ResFunctionalArea(SpaStructureTag, ResCommon, models.Model):
    _name = 'res.functional.area'
    _description = 'Functional Area'


class ResProgramGroup(SpaStructureTag, ResCommon, models.Model):
    _name = 'res.program.group'
    _description = 'Program Group'

    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        required=True,
    )


class ResProgram(SpaStructureTag, ResCommon, models.Model):
    _name = 'res.program'
    _description = 'Program'

    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        required=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Mission Area',
        related='program_group_id.functional_area_id',
        readonly=True,
        store=True,
    )
    spa_ids = fields.Many2many(
        'res.spa',
        'program_spa_rel',
        'spa_id',
        'program_id',
        string="SPA",
    )
    current_spa_id = fields.Many2one(
        'res.spa',
        string='Current SPA',
        compute='_compute_current_spa_id',
        help="Active SPA as of today",
    )
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
    )

    @api.one
    def _compute_current_spa_id(self):
        spas = self.env['res.spa'].search(
            [('id', 'in', self.spa_ids._ids),
             ('begin_date', '<=', fields.Date.context_today(self)),
             ('end_date', '>=', fields.Date.context_today(self)),
             ])
        self.current_spa_id = spas and spas[0] or False


class ResProjectGroup(SpaStructureTag, ResCommon, models.Model):
    _name = 'res.project.group'
    _description = 'Project Group'

    program_id = fields.Many2one(
        'res.program',
        string='Program',
        required=True,
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        related='program_id.program_group_id',
        readonly=True,
        store=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        related='program_id.functional_area_id',
        readonly=True,
        store=True,
    )


class ResProject(SpaStructureTag, ResCommon, models.Model):
    _name = 'res.project'
    _description = 'Project'

    date_start = fields.Date(
        string='Project Start Date',
    )
    # -- tag --
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        required=False,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Cost Center',
    )
    # -- start structure --
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
        required=True,
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        related='project_group_id.program_id',
        readonly=True,
        store=True,
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        related='project_group_id.program_group_id',
        readonly=True,
        store=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        related='project_group_id.functional_area_id',
        readonly=True,
        store=True,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_project_rel',
        'project_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )
    # program_rpt_id = fields.Many2one(
    #     'res.program',
    #     string='Report Program',
    # )
    # Other Info
    fund_type_id = fields.Many2one(
        'project.fund.type',
        string='Fund Type',
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
    )
    operation_id = fields.Many2one(
        'project.operation',
        string='Operation',
    )
    master_plan_id = fields.Many2one(
        'project.master.plan',
        string='Master Plan',
    )
    # prototype_ids = fields.One2many(
    #     'res.project.prototype',
    #     'project_id',
    #     string='Prototypes',
    # )


# class ResProjectPrototype(models.Model):
#     # TODO: remove this class, no longer use (just for avoid upgrade error)
#     _name = 'res.project.prototype'
#
#     project_id = fields.Many2one(
#         string='Project',
#         index=True,
#         ondelete='restrict',
#     )
#     name = fields.Char(
#         string='Name',
#         required=True,
#     )
#     code = fields.Char(
#         string='Code',
#         required=False,
#     )
#     prototype_type = fields.Selection(
#         [('research', 'Research'),
#          ('deliver', 'Deliver')],
#         string='Prototype Type',
#         required=True,
#     )
