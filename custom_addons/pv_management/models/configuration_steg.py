from odoo import fields , models ,api

class ConfigurationDistrictSteg(models.Model):
    _name = 'configuration.district.steg'
    _description = 'Configuration District STEG'

    name = fields.Char(string='Name', required=True)
    marque_onduleur = fields.Many2one('marque.onduleur', string='Marque Onduleur')
