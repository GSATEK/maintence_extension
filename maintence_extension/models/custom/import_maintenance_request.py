from odoo import models, fields, api
import base64
import xlrd
from datetime import datetime

class ImportMaintenanceWizard(models.TransientModel):
    _name = 'import.maintenance.wizard'
    _description = 'Import Maintenance Wizard'

    file = fields.Binary(string='File', required=True)
    file_name = fields.Char(string='File Name')

    def import_file(self):
        if not self.file:
            return

        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        maintenance_request = None

        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            vals_request = {}
            vals_task = {}

            try:
                planned_date = datetime(*xlrd.xldate_as_tuple(row[0].value, workbook.datemode)) if isinstance(row[0].value, float) else False
                if planned_date:
                    vals_request['schedule_date'] = planned_date
            except Exception as e:
                pass

            is_periodic_inspection = row[1].value == 'TRUE'
            vals_request['is_periodic_inspection'] = is_periodic_inspection

            try:
                expiration_date = datetime(*xlrd.xldate_as_tuple(row[2].value, workbook.datemode)) if isinstance(row[2].value, float) else False
                if expiration_date:
                    vals_request['expiration_date'] = expiration_date
            except Exception as e:
                pass

            responsible_email = row[3].value
            if responsible_email:
                responsible_user = self.env['res.users'].search([('email', '=', responsible_email)], limit=1)
                if responsible_user:
                    vals_request['user_id'] = responsible_user.id

            task_name = row[4].value
            if task_name:
                vals_task['name'] = task_name

            task_type = row[5].value
            if task_type:
                task_type_id = self.env['maintenance.type'].search([('name', '=', task_type)], limit=1).id
                if task_type_id:
                    vals_task['maintenance_tpye'] = task_type_id

            task_time = row[6].value
            if task_time:
                vals_task['time'] = task_time

            client_email = row[7].value
            client_name = row[8].value

            if client_email and client_name:
                client = self.env['res.partner'].search([('email', '=', client_email)], limit=1)
                if not client:
                    client = self.env['res.partner'].create({'name': client_name, 'email': client_email})

                equipment = self.env['maintenance.equipment'].search([('partner_id', '=', client.id)], limit=1)
                if not equipment:
                    equipment = self.env['maintenance.equipment'].create({
                        'name': f'Equipo de {client_name}',
                        'partner_id': client.id,
                        'equipment_assign_to': 'client'
                    })

                vals_request['equipment_id'] = equipment.id

            if vals_request and not maintenance_request:
                maintenance_request = self.env['maintenance.request'].create(vals_request)

            if vals_task and maintenance_request:
                vals_task['maintenance_request_id'] = maintenance_request.id
                self.env['maintenance.task'].create(vals_task)