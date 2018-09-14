# -*- coding: utf-8 -*-
from lxml import etree
from openerp import models, api, fields


class PABISecurity(models.Model):
    _name = 'pabi.security'

    name = fields.Char(
        string='Name',
        required=True,
        size=500,
    )
    date = fields.Datetime(
        string='Last Apply Date',
        readonly=True,
    )
    line_ids = fields.One2many(
        'pabi.security.line',
        'security_id',
        string='Security Line'
    )
    method = fields.Selection(
        [('by_user', 'Apply for each user'),
         ('all_user', 'Apply to all users'), ],
        string='Apply Method',
        required=True,
        default='by_user',
    )
    meta_group_id = fields.Many2one(
        'access.access',
        string='Meta Group',
    )
    group_id = fields.Many2one(
        'res.groups',
        string='User Group',
    )
    # Meta Groups Label
    mg1_label = fields.Char(string='MG1', compute='_compute_label')
    mg2_label = fields.Char(string='MG2', compute='_compute_label')
    mg3_label = fields.Char(string='MG3', compute='_compute_label')
    mg4_label = fields.Char(string='MG4', compute='_compute_label')
    mg5_label = fields.Char(string='MG5', compute='_compute_label')
    mg6_label = fields.Char(string='MG6', compute='_compute_label')
    mg7_label = fields.Char(string='MG7', compute='_compute_label')
    mg8_label = fields.Char(string='MG8', compute='_compute_label')
    mg9_label = fields.Char(string='MG9', compute='_compute_label')
    mg10_label = fields.Char(string='MG10', compute='_compute_label')
    # Groups
    g1_label = fields.Char(string='G1', compute='_compute_label')
    g2_label = fields.Char(string='G2', compute='_compute_label')
    g3_label = fields.Char(string='G3', compute='_compute_label')
    g4_label = fields.Char(string='G4', compute='_compute_label')
    g5_label = fields.Char(string='G5', compute='_compute_label')
    g6_label = fields.Char(string='G6', compute='_compute_label')
    g7_label = fields.Char(string='G7', compute='_compute_label')
    g8_label = fields.Char(string='G8', compute='_compute_label')
    g9_label = fields.Char(string='G9', compute='_compute_label')
    g10_label = fields.Char(string='G10', compute='_compute_label')
    g11_label = fields.Char(string='G11', compute='_compute_label')
    g12_label = fields.Char(string='G12', compute='_compute_label')
    g13_label = fields.Char(string='G13', compute='_compute_label')
    g14_label = fields.Char(string='G14', compute='_compute_label')
    g15_label = fields.Char(string='G15', compute='_compute_label')
    g16_label = fields.Char(string='G16', compute='_compute_label')
    g17_label = fields.Char(string='G17', compute='_compute_label')
    g18_label = fields.Char(string='G18', compute='_compute_label')
    g19_label = fields.Char(string='G19', compute='_compute_label')
    g20_label = fields.Char(string='G20', compute='_compute_label')
    g21_label = fields.Char(string='G21', compute='_compute_label')
    g22_label = fields.Char(string='G22', compute='_compute_label')
    g23_label = fields.Char(string='G23', compute='_compute_label')
    g24_label = fields.Char(string='G24', compute='_compute_label')
    g25_label = fields.Char(string='G25', compute='_compute_label')
    g26_label = fields.Char(string='G26', compute='_compute_label')
    g27_label = fields.Char(string='G27', compute='_compute_label')
    g28_label = fields.Char(string='G28', compute='_compute_label')
    g29_label = fields.Char(string='G29', compute='_compute_label')
    g30_label = fields.Char(string='G30', compute='_compute_label')

    @api.model
    def _get_used_field_list(self):
        """ Return meta group, group and its label as,
        [('mg1', 'MGroup 1'), ('mg2': 'MGroup 2'), ('g1', 'Group 1')]
        """
        field_list = []
        for m in ['access.access', 'res.groups']:
            groups = self.env[m].search([('pabi_security', '!=', False)],
                                        order='pabi_security')
            field_list += [(x.pabi_security, x.name) for x in groups]
        return field_list

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(PABISecurity, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            viewref = res['fields']['line_ids']['views']['tree']
            doc = etree.XML(viewref['arch'])
            # Find all used pabi_security
            field_list = self._get_used_field_list()
            for k, v in field_list:
                node = doc.xpath("//field[@name='%s']" % k)
                if node:
                    node[0].set('modifiers', '{"invisible": false}')
                    node[0].set('invisible', '0')
                    node[0].set('string', v)
            viewref['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def _compute_label(self):
        # Find all used pabi_security
        field_list = self._get_used_field_list()
        field_dict = dict(field_list)
        for rec in self:
            for i in ('mg', 'g'):  # mg and g
                for j in range(1, 11):  # 1-10
                    fn = '%s%s' % (i, j)
                    if field_dict.get(fn, False):
                        rec['%s_label' % fn] = field_dict[fn]
                    else:
                        rec['%s_label' % fn] = ""
        return True

    @api.model
    def _get_groups(self, group_model, line):
        """ There are 2 types of group, 1) meta, 2) normal """
        Group = self.env[group_model]
        groups = Group.search([('pabi_security', '!=', False)])
        g_dict = dict([(x.pabi_security, x.id) for x in groups])
        g_ids = []
        for f in line._fields.keys():
            if g_dict.get(f, False) and line[f]:
                g_ids.append(g_dict[f])
        groups = Group.search([('id', 'in', g_ids)])
        return groups

    @api.multi
    def apply_security(self):
        for rec in self:
            if rec.method == 'all_user':  # Apply to all users
                group_ids = [x.id for x in rec.meta_group_id.groups_id]
                if rec.group_id:
                    group_ids.append(rec.group_id.id)
                group_ids = [(4, x) for x in group_ids]
                all_users = self.env['res.users'].search([])
                print all_users.ids
                all_users.write({'groups_id': group_ids})
            elif rec.method == 'by_user':
                for line in rec.line_ids:
                    user_rec = line.user_id
                    user_rec.write({'groups_id': [(5,)]})
                    mg_groups = self._get_groups('access.access', line)
                    group_ids = \
                        [(4, x) for x in mg_groups.mapped('groups_id.id')]
                    # Apply Groups
                    res_groups = self._get_groups('res.groups', line)
                    group_ids += [(4, x) for x in res_groups.ids]
                    # Apply all groups to this user
                    user_rec.write({'groups_id': group_ids})
            rec.date = fields.Datetime.now()
        return True


class PABISecurityLine(models.Model):
    _name = 'pabi.security.line'

    security_id = fields.Many2one(
        'pabi.security',
        string='Security',
        readonly=True,
        index=True,
        ondelele='cascade',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
    )
    # Meta Groups
    mg1 = fields.Boolean(string='MG1', default=False)
    mg2 = fields.Boolean(string='MG2', default=False)
    mg3 = fields.Boolean(string='MG3', default=False)
    mg4 = fields.Boolean(string='MG4', default=False)
    mg5 = fields.Boolean(string='MG5', default=False)
    mg6 = fields.Boolean(string='MG6', default=False)
    mg7 = fields.Boolean(string='MG7', default=False)
    mg8 = fields.Boolean(string='MG8', default=False)
    mg9 = fields.Boolean(string='MG9', default=False)
    mg10 = fields.Boolean(string='MG10', default=False)
    # Groups
    g1 = fields.Boolean(string='G1', default=False)
    g2 = fields.Boolean(string='G2', default=False)
    g3 = fields.Boolean(string='G3', default=False)
    g4 = fields.Boolean(string='G4', default=False)
    g5 = fields.Boolean(string='G5', default=False)
    g6 = fields.Boolean(string='G6', default=False)
    g7 = fields.Boolean(string='G7', default=False)
    g8 = fields.Boolean(string='G8', default=False)
    g9 = fields.Boolean(string='G9', default=False)
    g10 = fields.Boolean(string='G10', default=False)
    g11 = fields.Boolean(string='G11', default=False)
    g12 = fields.Boolean(string='G12', default=False)
    g13 = fields.Boolean(string='G13', default=False)
    g14 = fields.Boolean(string='G14', default=False)
    g15 = fields.Boolean(string='G15', default=False)
    g16 = fields.Boolean(string='G16', default=False)
    g17 = fields.Boolean(string='G17', default=False)
    g18 = fields.Boolean(string='G18', default=False)
    g19 = fields.Boolean(string='G19', default=False)
    g20 = fields.Boolean(string='G20', default=False)
    g21 = fields.Boolean(string='G21', default=False)
    g22 = fields.Boolean(string='G22', default=False)
    g23 = fields.Boolean(string='G23', default=False)
    g24 = fields.Boolean(string='G24', default=False)
    g25 = fields.Boolean(string='G25', default=False)
    g26 = fields.Boolean(string='G26', default=False)
    g27 = fields.Boolean(string='G27', default=False)
    g28 = fields.Boolean(string='G28', default=False)
    g29 = fields.Boolean(string='G29', default=False)
    g30 = fields.Boolean(string='G30', default=False)


class AccessAccess(models.Model):
    _inherit = 'access.access'

    pabi_security = fields.Selection(
        [('mg1', 'MG1'), ('mg2', 'MG2'), ('mg3', 'MG3'), ('mg4', 'MG4'),
         ('mg5', 'MG5'), ('mg6', 'MG6'), ('mg7', 'MG7'), ('mg8', 'MG8'),
         ('mg9', 'MG9'), ('mg10', 'MG10'), ],
        string='PABI Group',
    )
    _sql_constraints = [
        ('pabi_security_uniq', 'unique(pabi_security)',
         'PABI Group must be unique!'),
    ]


class ResGroups(models.Model):
    _inherit = 'res.groups'

    pabi_security = fields.Selection(
        [('g1', 'G1'), ('g2', 'G2'), ('g3', 'G3'), ('g4', 'G4'),
         ('g5', 'G5'),  ('g6', 'G6'), ('g7', 'G7'), ('g8', 'G8'),
         ('g9', 'G9'), ('g10', 'G10'), ('g11', 'G11'), ('g12', 'G12'),
         ('g13', 'G13'), ('g14', 'G14'), ('g15', 'G15'), ('g16', 'G16'),
         ('g17', 'G17'), ('g18', 'G18'), ('g19', 'G19'), ('g20', 'G20'),
         ('g21', 'G21'), ('g22', 'G22'), ('g23', 'G23'), ('g24', 'G24'),
         ('g25', 'G25'), ('g26', 'G26'), ('g27', 'G27'), ('g28', 'G28'),
         ('g29', 'G29'), ('g30', 'G30'), ],
        string='PABI Group',
    )
    _sql_constraints = [
        ('pabi_security_uniq', 'unique(pabi_security)',
         'PABI Group must be unique!'),
    ]
