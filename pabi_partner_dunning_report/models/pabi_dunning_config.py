# -*- coding: utf-8 -*-
from openerp import fields, models, api, tools


class PABIDunningConfig(models.Model):
    _name = 'pabi.dunning.config'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    title_ids = fields.One2many(
        'pabi.dunning.config.title',
        'config_id',
        string='Prefix Mapping',
        #related='company_id.title_ids',
    )
    # Subject
    letter1_subject = fields.Char(
        string='Letter 1 Subject',
        #related='company_id.letter1_subject',
        translate=True,
    )
    letter2_subject = fields.Char(
        string='Letter 2 Subject',
        #related='company_id.letter2_subject',
        translate=True,
    )
    letter3_subject = fields.Char(
        string='Letter 3 Subject',
        #related='company_id.letter3_subject',
        translate=True,
    )
    # Letter 1
    letter1_header = fields.Text(
        string='Letter 1 Header',
        #related='company_id.letter1_header',
        translate=True,
    )
    letter1_footer = fields.Text(
        string='Letter 1 Footer',
        #related='company_id.letter1_footer',
        translate=True,
    )
    letter1_signature = fields.Text(
        string='Letter 1 Signature',
        #related='company_id.letter1_signature',
        translate=True,
    )
    # Letter 2
    letter2_header = fields.Text(
        string='Letter 2 Header',
        #related='company_id.letter2_header',
        translate=True,
    )
    letter2_footer = fields.Text(
        string='Letter 2 Footer',
        #related='company_id.letter2_footer',
        translate=True,
    )
    letter2_signature = fields.Text(
        string='Letter 2 Signature',
        #related='company_id.letter2_signature',
        translate=True,
    )
    # Letter 3
    letter3_header = fields.Text(
        string='Letter 3 Header',
        #related='company_id.letter3_header',
        translate=True,
    )
    letter3_footer = fields.Text(
        string='Letter 3 Footer',
        #related='company_id.letter3_footer',
        translate=True,
    )
    letter3_signature = fields.Text(
        string='Letter 3 Signature',
        #related='company_id.letter3_signature',
        translate=True,
    )
    sign_image = fields.Binary(
        string='Signature Image'
    )
    image_small = fields.Binary(string="Small-sized image",
                                store=False,
                                compute="_get_image",
                                help="Small sized image of this model. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field in form views or some kanban views.")
    
    @api.one
    @api.depends("sign_image")
    def _get_image(self):
        """ calculate the images sizes and set the images to the corresponding
            fields
        """
        image = self.sign_image

        data = tools.image_get_resized_images(image)
        self.image_medium = data["image_medium"]
        self.image_small = data["image_small"]
        return True


class PABIDunningConfigTitle(models.Model):
    _name = 'pabi.dunning.config.title'

    config_id = fields.Many2one(
        'pabi.dunning.config',
        string='Dunning Config',
        index=True,
        readonly=True,
    )
    title_id = fields.Many2one(
        'res.partner.title',
        string='Title',
        required=True,
    )
    new_title = fields.Char(
        string='New Title',
        required=True,
        size=500,
    )
