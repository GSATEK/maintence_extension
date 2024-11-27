from odoo import models, fields

class MaintenanceRoute(models.Model):
    _name = 'maintenance.route'
    _description = 'Maintenance Route'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    equipment_ids = fields.One2many('maintenance.equipment', 'route_id', string='Equipo')