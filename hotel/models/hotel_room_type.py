from odoo import fields, models


class HotelRoomType(models.Model):
    _name = 'hotel.room.type'
    _description = 'Hotel Room Type'

    name = fields.Char(string='Room Type', required=True)
    description = fields.Char(string='Description', required=True)

    room_ids = fields.One2many(
        'hotel.room',
        'room_type_id',
        string='Room Types')