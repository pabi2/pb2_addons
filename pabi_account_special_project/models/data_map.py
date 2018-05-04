# -*- coding: utf-8 -*-
from openerp import models, fields


class PABIDataMapType(models.Model):
    _inherit = 'pabi.data.map.type'

    # Add new type wil lbe used specifically for this addon
    app_name = fields.Selection(
        selection_add=[('special_project', 'Special Project')]
    )
