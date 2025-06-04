from odoo import fields, models

class HotelRoomEquipment(models.Model):
    _name = 'hotel.room.equipment'
    _description = 'Hotel Room Equipment'

    room_id = fields.Many2one('hotel.room', string='Room',required=True, ondelete='cascade')
    equipment_id = fields.Many2one('hotel.equipment', string='Equipment',required=True, ondelete='cascade')