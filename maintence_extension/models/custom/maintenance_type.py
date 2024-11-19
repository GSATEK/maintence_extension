from odoo import models, fields, _

class MaintenanceType(models.Model):
    _name = 'maintenance.type'
    _description = 'Maintenance Type'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')