from odoo import models, fields, api

class AlarmManagement(models.Model):
    _name = 'alarm.management'
    _description = 'Alarm Management'
    
    name = fields.Char(string='Name', required=True, translate=True)
    type = fields.Char(string='Type', translate=True)
    partie = fields.Selection([
        ('onduleur', 'Onduleur'),
        ('module', 'Module'),
        ('installation', 'Installation'),
        ('batterie', 'Batterie'),
        ('autre', 'Autre')
    ], string='Partie', required=True, translate=True)
    marque_onduleur_id = fields.Many2one('marque.onduleur', string='Marque Onduleur')
    code_alarm = fields.Char(string='Code Alarm', required=True, translate=True)

class MarqueOnduleur(models.Model):
    _name = 'marque.onduleur'
    _description = 'Marque Onduleur'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', translate=True)  # Optional identifier field
