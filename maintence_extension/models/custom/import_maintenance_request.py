import logging
from odoo import models, fields, api
import base64
import xlrd
from datetime import datetime

_logger = logging.getLogger(__name__)

class ImportMaintenanceWizard(models.TransientModel):
    _name = 'import.maintenance.wizard'
    _description = 'Import Maintenance Wizard'

    file = fields.Binary(string='Archivo', required=True)
    file_name = fields.Char(string='Nombre de archivo')

    def import_file(self):
        if not self.file:
            _logger.error("No file provided for import.")
            return

        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        maintenance_request = None

        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            vals_request = {}
            vals_task = {}
            vals_equipment = {}

            try:
                if len(row) > 0:
                    planned_date = datetime(*xlrd.xldate_as_tuple(row[0].value, workbook.datemode)) if isinstance(row[0].value, float) else False
                    if planned_date:
                        vals_request['schedule_date'] = planned_date
                        _logger.info(f"Planned date: {planned_date}")

                if len(row) > 1:
                    is_periodic_inspection = row[1].value == 'TRUE'
                    vals_request['is_periodic_inspection'] = is_periodic_inspection
                    _logger.info(f"Is periodic inspection: {is_periodic_inspection}")

                if len(row) > 2:
                    expiration_date = datetime(*xlrd.xldate_as_tuple(row[2].value, workbook.datemode)) if isinstance(row[2].value, float) else False
                    if expiration_date:
                        vals_request['expiration_date'] = expiration_date
                        _logger.info(f"Expiration date: {expiration_date}")

                if len(row) > 3:
                    responsible_email = row[3].value
                    if responsible_email:
                        responsible_user = self.env['res.users'].search([('email', '=', responsible_email)], limit=1)
                        if responsible_user:
                            vals_request['user_id'] = responsible_user.id
                            _logger.info(f"Responsible user: {responsible_user.id}")

                if len(row) > 4:
                    task_name = row[4].value
                    if task_name:
                        vals_task['name'] = task_name
                        _logger.info(f"Task name: {task_name}")

                if len(row) > 5:
                    task_type = row[5].value
                    if task_type:
                        task_type_id = self.env['maintenance.type'].search([('name', '=', task_type)], limit=1).id
                        if task_type_id:
                            vals_task['maintenance_tpye'] = task_type_id
                            _logger.info(f"Task type ID: {task_type_id}")

                if len(row) > 6:
                    task_time = row[6].value
                    if task_time:
                        vals_task['time'] = task_time
                        _logger.info(f"Task time: {task_time}")

                if len(row) > 7:
                    client_email = row[7].value
                    client_name = row[8].value
                    home = row[9].value
                    city = row[10].value
                    zip_code = row[11].value
                    url_google_maps = row[12].value
                    state_name = row[13].value
                    rae = row[14].value
                    contract_type = row[15].value
                    gestoria_email = row[16].value
                    equipment_speed_type = row[17].value

                    state_id = self.env['res.country.state'].search([('name', '=', state_name)], limit=1).id if state_name else False

                    if client_email and client_name:
                        client = self.env['res.partner'].search([('email', '=', client_email)], limit=1)
                        if not client:
                            client = self.env['res.partner'].create({
                                'name': client_name,
                                'email': client_email,
                                'city': city,
                                'zip': zip_code,
                                'state_id': state_id
                            })
                            _logger.info(f"Created client: {client.id}")
                        else:
                            if not client.city:
                                client.city = city
                            if not client.zip:
                                client.zip = zip_code
                            if not client.state_id:
                                client.state_id = state_id
                            _logger.info(f"Found client: {client.id}")

                        equipment = self.env['maintenance.equipment'].search([('serial_no', '=', rae)], limit=1)
                        if not equipment:
                            _logger.info(f"Creating equipment for client: {client.id}")
                            equipment = self.env['maintenance.equipment'].create({
                                'name': f'ascensor {client_name}',
                                'partner_id': client.id,
                                'equipment_assign_to': 'client',
                                'serial_no': rae,
                                'home': home,
                                'city': city,
                                'zip': zip_code,
                                'state_id': state_id,
                                'google_maps_link': url_google_maps,
                                'equipment_speed_type': 'high_speed' if equipment_speed_type == 'Alta velocidad' else 'low_speed'
                            })
                            _logger.info(f"Created equipment: {equipment.id}")
                        else:
                            if not equipment.home:
                                equipment.home = home
                            if not equipment.city:
                                equipment.city = city
                            if not equipment.zip:
                                equipment.zip = zip_code
                            if not equipment.state_id:
                                equipment.state_id = state_id
                            if not equipment.google_maps_link:
                                equipment.google_maps_link = url_google_maps
                            if not equipment.equipment_speed_type:
                                equipment.equipment_speed_type = 'high_speed' if equipment_speed_type == 'Alta velocidad' else 'low_speed'
                            _logger.info(f"Found equipment: {equipment.id}")

                        vals_request['equipment_id'] = equipment.id

                    if gestoria_email:
                        gestoria = self.env['res.partner'].search([('email', '=', gestoria_email)], limit=1)
                        if gestoria:
                            vals_request['manager_id'] = gestoria.id
                            _logger.info(f"Gestoria: {gestoria.id}")

                    vals_request['contract_type'] = contract_type
                    _logger.info(f"Contract type: {contract_type}")

                _logger.info(f"vals_request: {vals_request}")

                if vals_request and not maintenance_request:
                    maintenance_request = self.env['maintenance.request'].create(vals_request)
                    _logger.info(f"Created maintenance request: {maintenance_request.id}")

                if vals_task and maintenance_request:
                    vals_task['maintenance_request_id'] = maintenance_request.id
                    self.env['maintenance.task'].create(vals_task)
                    _logger.info(f"Created maintenance task for request: {maintenance_request.id}")

            except IndexError as e:
                _logger.error(f"IndexError: {e}")
                continue
            except Exception as e:
                _logger.error(f"Unexpected error: {e}")
                continue
