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
        addon = 'pabi_budget_report'
        template_ids = [
            'xlsx_report_budget_summary'
        ]
        file_dir = os.path.dirname(os.path.realpath(__file__))
        env['ir.attachment'].load_xlsx_template(addon, template_ids, file_dir)
