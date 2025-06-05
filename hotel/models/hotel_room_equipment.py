from odoo import fields, models,api,_
from odoo.exceptions import ValidationError

class HotelRoomEquipment(models.Model):
    _name = 'hotel.room.equipment'
    _description = 'Hotel Room Equipment'

    room_id = fields.Many2one('hotel.room', string='Room',required=True, ondelete='cascade')
    equipment_id = fields.Many2one('hotel.equipment', string='Equipment',required=True, ondelete='cascade')

    _sql_constraints = [
        (
            'unique_room_equipment',
            'UNIQUE(room_id, equipment_id)',
            "The same equipment can only be added once in a room."
        )
    ]
