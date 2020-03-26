# -*- coding: utf-8 -*-
from openerp import models, fields, api

""" IDs ของกลุ่มที่มีการเปลี่ยนจากตำแหน่ง ... -> ตำแหน่ง ... """
GROUPS_IDS = [16, 22, 30, 31, 35, 58, 70, 72, 73, 74]


class AuditlogLog(models.Model):
    _inherit = 'auditlog.log'

    is_groups_id = fields.Boolean(default=False)
    is_lang = fields.Boolean(default=False)
    is_active = fields.Boolean(default=False)


class AuditlogLogLine(models.Model):
    _inherit = 'auditlog.log.line'

    difference_value = fields.Text(
        string='Difference Value',
        compute='_compute_difference_value_text',
        store=True,
    )
    old_difference_value_text = fields.Text(
        string='Diff Remove',
        compute='_compute_difference_value_text',
        store=True,
    )
    new_difference_value_text = fields.Text(
        string='Diff Add',
        compute='_compute_difference_value_text',
        store=True,
    )

    @api.multi
    @api.depends('field_id', 'old_value_text', 'new_value_text')
    def _compute_difference_value_text(self):
        for line in self:
            if line.field_name != 'groups_id':
                continue
            add = []
            remove = []
            groups_old = []
            groups_new = []
            """ เปลี่ยน type unicode"""
            values_old = eval(line.old_value_text)
            values_new = eval(line.new_value_text)
            """ หาค่าที่ต่างกันจาก Old และ New"""
            diff_values = list(
                set(values_old).union(set(values_new)) -
                set(values_old).intersection(set(values_new))
            )
            diff_datas = [x[0] for x in diff_values]
            new_datas = [x[0] for x in values_new]
            old_datas = [x[0] for x in values_old]
            """ for นี้สำหรับแบ่งกลุ่มของข้อมูลว่า กลุ่มไหนเป็นกลุ่ม
                ที่อยู่ในข้อมูลใหม่ หรือกลุ่มเก่า
                *** groups_old หมายถึง กลุ่มเก่า ก่อนที่จะเปลี่ยนค่า
                *** groups_new หมายถึง กลุ่มใหม่ หลังจากที่เปลี่ยนค่า """
            for data in diff_datas:
                if data in old_datas:
                    groups_old.append(data)
                if data in new_datas:
                    groups_new.append(data)
            if groups_old:
                add, remove = self._add_text(
                    new_datas, groups_old, add, remove
                )
            if groups_new:
                remove, add = self._add_text(
                    old_datas, groups_new, remove, add
                )
            line.difference_value = diff_values
            line.new_difference_value_text = "%s" % ", ".join(add)
            line.old_difference_value_text = "%s" % ", ".join(remove)

    """ ที่ฟังก์ชัน _add_text จะ return text_1, text_2
        text_1 สำหรับกลุ่มที่เปลี่ยนจากตำแหน่งสูง -> ต่ำ
        text_2 สำหรับกลุ่มที่มีการเปลี่ยนแปลงสิทธิ์ """
    @api.multi
    def _add_text(self, datas, groups_data, text_1, text_2):
        Group = self.env['res.groups']
        with_implied_ids = self._check_category_group(groups_data)
        """ ถ้าหากว่า with_implied_ids != False
            แสดงว่าในกลุ่มที่มีการเปลี่ยนแปลงค่า มีบางกลุ่มที่มีการเปลี่ยน
            จากตำแหน่ง A -> B

            ถ้าหากว่า with_implied_ids = False
            แสดงว่าในกลุ่มที่มีการเปลี่ยนแปลงค่า ไม่มีกลุ่มที่มีการเปลี่ยน
            จากตำแหน่ง A -> B """
        if with_implied_ids:
            """ ค้นหากลุ่มใน groups_data ที่มีการเปลี่ยนจาก A -> B """
            groups = Group.search([
                ('category_id', 'in', with_implied_ids),
                ('id', 'in', groups_data)
            ])
            """ mapped implied_ids ของกลุ่มทั้งหมด """
            implied_ids = groups.mapped('implied_ids').ids
            """ หาว่า implied_ids มีกลุ่มไหนที่อยู่ใน datas บ้าง
            โดย datas จะแยกเป็น 2 ประเภท
                - 1.old_datas (ข้อมูลเก่า ก่อนที่จะเปลี่ยนค่า)
                - 2.new_datas (ข้อมูลใหม่ หลังจากที่เปลี่ยนค่า)
            ถ้า intersection แล้วอยู่ใน old_datas
            แสดงว่าเป็นการเปลี่ยนจากตำแหน่งสูงกว่า -> ตำแหน่งที่ต่ำกว่า
            เพราะหลังจากเปลี่ยนแปลง  ข้อมูลเก่ามีข้อมูล แต่ข้อมูลใหม่ไม่มี
            จึงเป็นการเปลี่ยนจากตำแหน่งสูงกว่า -> ตำแหน่งที่ต่ำกว่า

            ถ้า intersection แล้วอยู่ใน new_datas
            แสดงว่าเป็นการเปลี่ยนจากตำแหน่งต่ำกว่า -> ตำแหน่งที่สูงกว่า
            เพราะหลังจากเปลี่ยน  ข้อมูลเก่าไม่มีข้อมูล แต่ข้อมูลใหม่มี
            จึงเป็นการเปลี่ยนจากตำแหน่งต่ำกว่า -> ตำแหน่งที่สูงกว่า """
            group_id = list(set(datas).intersection(
                set(implied_ids)
            ))
            """ เป็นการวนเพื่อเติมข้อความเฉพาะ !!! กลุ่มที่มีการเปลี่ยนจาก !!!
            สูง -> ต่ำ หรือ ต่ำ -> สูงเท่านั้น
            ถ้าเปลี่ยนจากสูงไปต่ำ จะเป็นข้อความ ADD - ตำแหน่งที่ต่ำ
            ถ้าเปลี่ยนจากต่ำไปสูง จะเป็นข้อความ REMOVE - ตำแหน่งที่สูง """
            for group in Group.browse(group_id):
                categ_name = ''
                group_name = ''
                if group.category_id.name:
                    categ_name = group.category_id.name + " / "
                if group.name:
                    group_name = group.name
                text_1.append(categ_name + group_name)
        """ เป็นการวนเพื่อเติมข้อความ
        กลุ่มที่มีการเปลี่ยนจากมีสิทธิ์ หรือไม่มีสิทธิ์ """
        for group in Group.browse(groups_data):
            categ_name = ''
            group_name = ''
            if group.category_id.name:
                categ_name = group.category_id.name + " / "
            if group.name:
                group_name = group.name
            text_2.append(categ_name + group_name)
        return text_1, text_2

    """ ฟังก์ชันหากลุ่มที่เปลี่ยนกลุ่มไหนที่มี Implied_is
        สนใจเฉพาะกลุ่มที่มี category_id อยู่ใน GROUP_IDS เท่านั้น
        เพราะเป็นกลุ่มที่มีการเปลี่ยนจาก ตำแหน่ง A -> B
        เพราะกลุ่มอื่นๆจะเป็นการเปลี่ยนจากมีสิทธิ์ -> ไม่มีสิทธิ์
        และจะคืนค่า IDs ของ category_id ตามเงื่อนไขที่กล่าว """
    @api.multi
    def _check_category_group(self, data):
        Group = self.env['res.groups']
        with_implied_ids = []
        data_ids = [x.category_id.id for x in Group.browse(data)]
        for id in list(set(data_ids)):
            if id not in GROUPS_IDS:
                continue
            with_implied_ids.append(id)
        return with_implied_ids


class AuditlogRule(models.Model):
    _inherit = 'auditlog.rule'

    def _create_log_line_on_write(self, log, fields_list, old_values, new_values):
        res = super(AuditlogRule, self)._create_log_line_on_write(
                log, fields_list, old_values, new_values)
        vals = {'is_groups_id': False, 'is_lang': False, 'is_active': False}
        for rec in log.line_ids:
            if rec.field_id.name == 'groups_id':
                vals.update({'is_groups_id': True})
            if rec.field_id.name == 'lang':
                vals.update({'is_lang': True})
            if rec.field_id.name == 'active':
                vals.update({'is_active': True})
        log.write(vals)
        return res
