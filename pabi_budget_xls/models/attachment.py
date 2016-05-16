# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import \
    models, fields, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    budget_template = fields.Boolean('Budget Template')

