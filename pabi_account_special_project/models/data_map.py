# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PABIDataMap(models.Model):
    _inherit = 'pabi.data.map'

    type = fields.Selection(
        selection_add=[('special_project', 'Special Project')],
    )
