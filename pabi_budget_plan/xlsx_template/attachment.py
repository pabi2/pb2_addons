# -*- coding: utf-8 -*-
import logging
import os

from openerp import models, fields, api, _
from openerp import tools
from openerp.exceptions import ValidationError
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def init(self, cr):
        """ Load all files to ir.attachment (from same directory) """
        env = api.Environment(cr, SUPERUSER_ID, {})
        addon = 'pabi_budget_plan'
        template_ids = [
            'budget_plan_unit_base_xlsx_template',
            'budget_breakdown_unit_base_xlsx_template',
            'invest_asset_plan_xlsx_template',
            # 'budget_plan_invest_construction_xlsx_template',
            'budget_plan_project_base_xlsx_template',
        ]
        file_dir = os.path.dirname(os.path.realpath(__file__))
        env['ir.attachment'].load_xlsx_template(addon, template_ids, file_dir)
