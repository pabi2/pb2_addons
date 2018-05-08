# -*- coding: utf-8 -*-
from openerp import fields, models


class ResSection(models.Model):
    _inherit = 'res.section'

    purchasing_unit_id = fields.Many2many(
        'wkf.config.purchase.unit',
        'purchasingunit_section_rel',
        'section_id',
        'purchasing_unit_id',
        string='Purchasing Unit',
    )
    boss_ids = fields.One2many(
        'wkf.cmd.boss.level.approval',
        'section_id',
        string='Boss Level Approval',
    )
