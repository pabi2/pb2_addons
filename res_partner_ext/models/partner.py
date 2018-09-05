# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv.expression import get_unaccent_wrapper


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'search_key'

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    name = fields.Char(
        translate=True,
    )
    create_date = fields.Datetime(
        readonly=True,
    )
    search_key = fields.Char(
        string='Search Key',
        index=True,
        compute='_get_search_key',
        store=True,
    )
    require_taxid = fields.Boolean(
        string='Require Tax ID',
        compute='_get_require_taxbranch',
        store=True,
        multi='taxbranch',
    )
    require_taxbranch = fields.Boolean(
        string='Require Tax Branch ID',
        compute='_get_require_taxbranch',
        store=True,
        multi='taxbranch',
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Supplier Category',
        required=True,
    )
    tag_ids = fields.Many2many(
        'res.partner.tag',
        string='Tags',
    )
    require_receivable_account = fields.Boolean(
        string='Require Receivable Account',
        related='category_id.require_receivable_account',
    )
    require_payable_account = fields.Boolean(
        string='Require Payable Account',
        related='category_id.require_payable_account',
    )
    title_lang = fields.Char(
        string='Title (lang)',
        compute='_compute_title_lang',
    )
    display_name2 = fields.Char(
        string='Name',
        compute='_compute_display_name2',
        store=True,
        help="Name with title",
    )
    customer_legacy_code = fields.Char(
        string='Customer Legacy Code',
    )
    supplier_legacy_code = fields.Char(
        string='Supplier Legacy Code',
    )

    @api.onchange('title')
    def _onchange_title(self):
        title_name = False
        if self._context.get('lang', False) == 'th_TH':
            title_name = self.title.with_context(lang='en_US').name_get()
        if self._context.get('lang', False) == 'en_US':
            title_name = self.title.with_context(lang='th_TH').name_get()
        self.title_lang = title_name and title_name[0][1] or False

    @api.multi
    @api.depends('title', 'name')
    def _compute_display_name2(self):
        for rec in self:
            name = [rec.title.name, rec.name]
            name = filter(lambda a: a is not False, name)
            rec.display_name2 = ' '.join(name)

    @api.multi
    def _compute_title_lang(self):
        trans_dict = {}
        titles = self.mapped('title')
        if self._context.get('lang', False) == 'th_TH':
            trans_dict = dict(titles.with_context(lang='en_US').name_get())
        if self._context.get('lang', False) == 'en_US':
            trans_dict = dict(titles.with_context(lang='th_TH').name_get())
        for rec in self:
            rec.title_lang = trans_dict.get(rec.title.id)

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_id and active_model == 'res.partner':
            partner = self.browse(active_id)
            if not partner.category_id.default_parent_vat:
                res.remove('vat')
        return res

    @api.multi
    @api.constrains('vat', 'taxbranch', 'category_id', 'name')
    def _check_vat_taxbranch_unique(self):
        for rec in self:
            if not rec.category_id:
                raise ValidationError(_('No partner category is provided.'))
            elif rec.category_id.require_tax_branch_unique:
                partners = self.search([('vat', '=', rec.vat),
                                        ('taxbranch', '=', rec.taxbranch)])
                if len(partners) > 1:
                    raise ValidationError(_(
                        "Tax ID + Tax Branch ID must be unique!"))

    @api.multi
    @api.constrains('vat')
    def _check_vat(self):
        for rec in self:
            if rec.require_taxid and rec.vat > 0 and len(rec.vat) != 13:
                raise ValidationError(_("Tax ID must be 13 digits!"))

    @api.multi
    @api.constrains('taxbranch')
    def _check_taxbranch(self):
        for rec in self:
            if rec.require_taxbranch and rec.taxbranch > 0 and \
                    len(rec.taxbranch) != 5:
                raise ValidationError("Tax Branch ID must be 5 digits!")

    @api.multi
    @api.constrains('is_company', 'parent_id', 'child_ids')
    def _check_is_company(self):
        for rec in self:
            if not rec.is_company and rec.child_ids:
                raise ValidationError(
                    _("A contact must not have child companies"))

    @api.multi
    @api.constrains('name')
    def _check_partner_name(self):
        for rec in self:
            if rec.category_id.check_partner_name_unique:
                partners = self.search([('is_company', '=', True),
                                        ('parent_id', '=', False),
                                        ('name', '=', rec.name),
                                        '|', ('supplier', '=', True),
                                        ('customer', '=', True)])
                if len(partners) > 1:
                    raise ValidationError(_("Partner name must be unique!"))

    @api.multi
    @api.constrains('child_ids', 'name')
    def _check_contact_name_unique(self):
        for rec in self:
            # Edit from company's contact
            if rec.child_ids and rec.category_id.check_contact_name_unique:
                names = rec.child_ids.mapped('name')
                counter = {x: names.count(x) for x in names}
                for count in counter.values():
                    if count > 1:
                        raise ValidationError(
                            _("Contact name must be unique!"))
            # Edit from contact itself
            if rec.parent_id and \
                    rec.parent_id.category_id.check_contact_name_unique:
                partners = self.search([('parent_id', '=', rec.parent_id.id),
                                        ('name', '=', rec.name)])
                if len(partners) > 1:
                    raise ValidationError(_("Contact name must be unique!"))

    @api.model
    def create(self, vals):
        if not vals.get('category_id', False):
            vals['category_id'] = \
                self.env.user.company_id.default_employee_partner_categ_id.id
        partner = super(ResPartner, self).create(vals)
        # Always use same tag as parent.
        if vals.get('parent_id', False):
            partner.category_id = partner.parent_id.category_id
        return partner

    @api.model
    def create_partner(self, vals):
        try:
            WS = self.env['pabi.utils.ws']
            res = WS.friendly_create_data(self._name, vals)
            if res['is_success']:
                res_id = res['result']['id']
                p = self.browse(res_id)
                # overwrite partner's account with categ's account
                p.write({
                    'property_account_payable':
                    p.category_id.payable_account_id.id,
                    'property_account_receivable':
                    p.category_id.receivable_account_id.id,
                    # Force customer / supplier = true
                    'supplier': True,
                    'customer': True,
                    })
                res['result']['name'] = p.name
                res['result']['search_key'] = p.search_key
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        return res

    @api.model
    def create_update_partner(self, vals):
        # No search key, do create, else try to update.
        if not vals.get('search_key', False):
            return self.create_partner(vals)
        try:  # Update
            WS = self.env['pabi.utils.ws']
            res = WS.friendly_update_data(self._name, vals, 'search_key')
            if res['is_success']:
                res_id = res['result']['id']
                p = self.browse(res_id)
                res['result']['name'] = p.name
                res['result']['search_key'] = p.search_key
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        return res

    @api.model
    def _pre_category_change(self, vals):
        # Do not allow change of partner tag,
        # if it result in change of its accounting
        company = self.env.user.company_id
        check = company.no_partner_tag_change_account
        if check and vals.get('category_id', False):
            # Test whether index exists to prevent exception
            category = vals.get('category_id')
            if not category:
                return
            for partner in self:
                prev_categ = partner.category_id
                new_category_id = category
                new_categ = \
                    self.env['res.partner.category'].browse(new_category_id)
                if prev_categ:
                    if ((prev_categ.receivable_account_id !=
                         new_categ.receivable_account_id) or
                        (prev_categ.payable_account_id !=
                         new_categ.payable_account_id)):
                        raise ValidationError(
                            _("Changing of Partner Tag is not allowed, as it "
                              "will result in changing of its account code"))

    @api.model
    def _post_category_change(self, vals):
        # Parent's tag change, force change to all childs
        if vals.get('category_id', False):
            for partner in self:
                if partner.child_ids:
                    for child in partner.child_ids:
                        child.category_id = partner.category_id

    @api.multi
    def write(self, vals):
        # self._pre_category_change(vals)  # Do not need this
        res = super(ResPartner, self).write(vals)
        self._post_category_change(vals)
        return res

    @api.v7
    def onchange_address(self, cr, uid, ids,
                         use_parent_address, parent_id, context=None):
        result = super(ResPartner, self).onchange_address(cr, uid, ids,
                                                          use_parent_address,
                                                          parent_id,
                                                          context=context)
        parent = self.browse(cr, uid, parent_id, context=context)
        category_id = parent.category_id.id or False
        if category_id:
            if result.get('value', False):
                result['value'].update(
                    {'category_id': category_id})
            else:
                result.update(
                    {'value': {'category_id': category_id}})
        return result

    @api.multi
    @api.depends('category_id', 'parent_id')
    def _get_require_taxbranch(self):
        for rec in self:
            if rec.parent_id:  # If a contact, never set as required.
                rec.require_taxid = False
                rec.require_taxbranch = False
            elif rec.category_id:
                rec.require_taxid = rec.category_id.require_taxid
                rec.require_taxbranch = rec.category_id.require_taxbranch

    @api.multi
    @api.depends('name')
    def _get_search_key(self):
        for rec in self:
            if type(rec.id) in (int,):
                rec.search_key = '%0*d' % (7, rec.id)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            if self.category_id.receivable_account_id:
                self.property_account_receivable = \
                    self.category_id.receivable_account_id.id
            if self.category_id.payable_account_id:
                self.property_account_payable = \
                    self.category_id.payable_account_id.id
            if self.category_id.fiscal_position_id:
                self.property_account_position = \
                    self.category_id.fiscal_position_id.id
        else:
            self.property_account_receivable = False
            self.property_account_payable = False
            self.property_account_position = False

    @api.multi
    def name_get(self):
        """ Overwrite method, just to add Title """
        res = []
        for record in self:
            if record.title:
                name = "%s %s" % (record.title.name, record.name)
            else:
                name = record.name
            if record.search_key:
                name = '[%s] %s' % (record.search_key, name)
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, name)
            if self._context.get('show_address_only'):
                name = self._display_address(record, without_company=True)
            if self._context.get('show_address'):
                name = name + "\n" + \
                    self._display_address(record, without_company=True)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if self._context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=100):
        """ Overwrite base class, to remove order by display_name """
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params = \
                where_query.get_sql()
            where_str = where_clause and \
                (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent})
                     -- ORDER BY {display_name}
                    """.format(where=where_str, operator=operator,
                               email=unaccent('email'),
                               display_name=unaccent('display_name'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name, search_name]
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())

            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []

        ids = self.search(cr, uid, [], limit=limit)  # Just return all
        return self.name_get(cr, uid, ids, context)


class ResPartnerCategory(models.Model):

    _inherit = 'res.partner.category'

    parent_id = fields.Many2one(
        'res.partner.category',
        domain="[('parent_id', '=', False)]",
    )
    require_payable_account = fields.Boolean(
        string='Require Payable Account',
        default=True,
    )
    payable_account_id = fields.Many2one(
        'account.account',
        string='Account Payable',
        domain="[('type', '=', 'payable')]",
        help="This account will be used as default payable account "
        "for a partner, when it is being created.",
    )
    require_receivable_account = fields.Boolean(
        string='Require Receivable Account',
        default=True,
    )
    receivable_account_id = fields.Many2one(
        'account.account',
        string='Account Receivable',
        domain="[('type', '=', 'receivable')]",
        help="This account will be used as default receivable account "
        "for a partner, when it is being created.",
    )
    property_account_receivable = fields.Many2one(
        'account.account',
        required=False,
    )
    property_account_payable = fields.Many2one(
        'account.account',
        required=False,
    )
    require_taxid = fields.Boolean(
        string='Require Tax ID',
        default=False,
        help="When create partner in this category, always require Tax ID",
    )
    require_taxbranch = fields.Boolean(
        string='Require Tax Branch ID',
        default=False,
        help="When create partner in this category, "
        "always require Tax Branch ID",
    )
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Default Fiscal Position',
        help="For customer with this Partner Tag, "
        "it will be default with this Fiscal Position",
    )
    require_tax_branch_unique = fields.Boolean(
        string='Validate Tax/Branch Unique',
        help="Non-Government, checking this flag will ensure that Tax ID "
        "and Branch combination must be unique per company of this category",
    )
    check_partner_name_unique = fields.Boolean(
        string='Unique Partner Name',
        default=True,
        help="When create this partner, validate for name uniqueness",
    )
    check_contact_name_unique = fields.Boolean(
        string='Unique Contact Names',
        default=True,
        help="When create this partner, validate for name uniqueness",
    )
    default_parent_vat = fields.Boolean(
        string="Default with Company's Tax ID",
        default=True,
        help="For a contact, we can set to use parent tax id by default",
    )

    @api.multi
    def name_get(self):
        res = []
        for category in self:
            res.append((category.id, category.name))
        return res

    @api.onchange('require_receivable_account')
    def _onchange_require_receivable_account(self):
        self.receivable_account_id = False

    @api.onchange('require_payable_account')
    def _onchange_require_payable_account(self):
        self.payable_account_id = False


class ResPartnerTag(models.Model):
    _description = 'Partner Tags'
    _name = 'res.partner.tag'

    name = fields.Char(
        string='Name',
        required=True,
    )
    parent_id = fields.Many2one(
        'res.partner.tag',
        string='Parent Tag',
    )
    child_ids = fields.One2many(
        'res.partner.tag',
        'parent_id',
        string='Child Tags',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
