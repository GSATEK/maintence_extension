from odoo import models, fields, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'


    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee'), ('client', 'Cliente'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee'
    )
    partner_id = fields.Many2one('res.partner', string='Cliente')
    equipment_speed_type = fields.Selection(
        [('high_speed', 'Alta velocidad'), ('low_speed', 'Baja velocidad')],
        string='Tipo de aparato'
    )
    street = fields.Char(string='Calle')
    city = fields.Char(string='Ciudad')
    zip = fields.Char(string='Código postal')
    state_id = fields.Many2one('res.country.state', string='Provincia')
    home = fields.Char(string='Domicilio')
    google_maps_link = fields.Char(string='Enlace a Google Maps')
    route_id = fields.Many2one('maintenance.route', string='Ruta')

