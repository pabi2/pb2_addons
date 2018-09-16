# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class Pb2BossView(models.Model):
    _name = 'pb2.boss.view'
    _description = 'View for Alfresco Approval Level'
    _auto = False

    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
    lvl = fields.Char(
        string='Level',
    )
    amount_max = fields.Float(
        string='Maximum',
    )
    amount_max_emotion = fields.Float(
        string='Maximum (Emo)',
    )
    first_name = fields.Char(
        string='Fisrt Name',
    )
    last_name = fields.Char(
        string='Last Name',
    )
    doc_type = fields.Char(
        string='Doc Type',
    )
    is_special = fields.Char(
        string='Is Special',
    )
    employee_code = fields.Char(
        string='Employee Code'
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        _sql = """
            SELECT row_number() over (order by amount_max, is_special) as id, *
            FROM (
                    SELECT a.org_id, a.section_id,
                        a.employee_id, a._level AS lvl,
                        a.amount_max, a.amount_max_emotion,
                        a.first_name, a.last_name,
                        a.doc_type, '0'::text AS is_special,
                        a.employee_code
                FROM (
                    SELECT b.org_id, b.section_id, b.employee_id,
                        l.name AS _level,
                        a_1.amount_max, a_1.amount_max_emotion,
                        h.employee_code,
                        h.first_name, h.last_name, d.name AS doc_type,
                        '0' AS is_special, l.id AS level_id
                    FROM wkf_cmd_level l,
                        wkf_cmd_boss_level_approval b,
                        wkf_cmd_approval_amount a_1,
                        hr_employee h,
                        wkf_config_doctype d
                    WHERE l.id = b.level AND a_1.org_id = b.org_id AND
                        a_1.level = b.level AND a_1.doctype_id = d.id AND
                        b.employee_id = h.id AND
                        a_1.amount_max > 0::double precision
                ) a
                LEFT JOIN wkf_cmd_boss_special_level s ON
                    a.section_id = s.section_id AND
                    s.special_level = a.level_id
                WHERE s.id IS NULL
                UNION -- CURRENTLY, Special Level is not used (for ref only)
                SELECT s.org_id, sl.section_id, sl.employee_id, l.name AS lvl,
                    a.amount_max, a.amount_max_emotion,
                    h.first_name, h.last_name,
                    d.name AS doc_type, '1'::text AS is_special,
                    h.employee_code
                FROM wkf_cmd_level l,
                    wkf_cmd_boss_special_level sl,
                    res_section s,
                    wkf_cmd_approval_amount a,
                    hr_employee h,
                    wkf_config_doctype d
                WHERE l.id = sl.special_level AND sl.section_id = s.id AND
                    a.org_id = s.org_id AND a.level = sl.special_level AND
                    a.doctype_id = d.id AND sl.employee_id = h.id AND
                    a.amount_max > 0::double precision
                ORDER BY 5, 10 DESC) b
        """

        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql,))
