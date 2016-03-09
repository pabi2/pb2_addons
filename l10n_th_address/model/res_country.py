# -*- coding: utf-8 -*-

from openerp import models, fields

class ResCountry(models.Model):

    _inherit = 'res.country'
    
    name_en = fields.Char(string='Country (en)', required=False)
    
class ResCountryProvince(models.Model):

    _name = 'res.country.province'
    _description = 'Provinces'
    
    name = fields.Char(string='Province', required=True)
    name_en = fields.Char(string='Province (en)', required=False)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    

class ResCountryDistrict(models.Model):

    _name = 'res.country.district'
    _description = 'Districts'
    
    name = fields.Char(string='District', required=True)
    name_en = fields.Char(string='District (en)', required=False)
    province_id = fields.Many2one('res.country.province', string='Province', required=True)

class ResCountryTownship(models.Model):

    _name = 'res.country.township'
    _description = 'Township'
    
    name = fields.Char(string='Township', required=True)
    name_en = fields.Char(string='Township (en)', required=False)
    district_id = fields.Many2one('res.country.district', string='District', required=True)
    zip = fields.Char(string='Zip')
    province_id = fields.Many2one(
                'res.country.province', 
                related='district_id.province_id', 
                string='Province', 
                readonly=True, 
                store=True)
    country_id = fields.Many2one(
                'res.country', 
                related='district_id.province_id.country_id', 
                string='Country', 
                readonly=True, 
                store=True)
