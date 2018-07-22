# -*- coding: utf-8 -*-
from openerp import models, api, fields


class PABISecurity(models.Model):
    _name = 'pabi.security'

    name = fields.Char(
        string='Name',
        required=True,
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
            for line in rec.line_ids:
                user_rec = line.user_id
                user_rec.write({'groups_id': []})  # Clear groups first
                # Apply Meta Groups
                mg_groups = self._get_groups('access.access', line)
                group_ids = [(4, x) for x in mg_groups.mapped('groups_id.id')]
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
