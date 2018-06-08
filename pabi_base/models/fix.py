# -*- coding: utf-8 -*-
from openerp import models, api


class ResSection(models.Model):
    _inherit = 'res.section'

    @api.model
    def fix_section_nstda_fund(self):
        """ Auto add NSTDA fund to all section (if not exists) """
        sections = self.search([('fund_ids', '=', [])])
        for section in sections:
            section.fund_ids = self.env.ref('base.fund_nstda')
