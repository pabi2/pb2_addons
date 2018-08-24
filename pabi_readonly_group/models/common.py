# -*- coding: utf-8 -*-
from openerp import api
from lxml import etree


class ReadonlyCommon(object):

    @api.model
    def set_right_readonly_group(self, res):
        readonly_group = 'pabi_readonly_group.group_readonly_%s' % self._table
        if self.env.user.has_group(readonly_group):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            root.set('edit', 'false')
            root.set('delete', 'false')
            nodes = root.xpath("//button")
            # nodes_show = root.xpath(
            #     "//div[@class='oe_right oe_button_box']//button")
            for node in nodes:
                node.set('modifiers', '{"invisible": true}')
            res['arch'] = etree.tostring(root)
        return res
