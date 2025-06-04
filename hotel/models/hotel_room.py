from odoo import fields, models

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'

    name = fields.Char(string='Hotel Room Name', required=True)
    description = fields.Text(string='Hotel Room Description')
    base_price = fields.Float(string='Hotel Room Base Price')
    max_allowed_person = fields.Integer(string='Hotel Room Max Allowed', required=True,default=2)
    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
    ], string="State", default='available', store=True)

    room_type_id = fields.Many2one(
        'hotel.room.type',
        string='Hotel Room Type',
        required=True,
    )
    room_equipment_ids = fields.One2many(
        'hotel.room.equipment',
        'room_id',
        string='Equipments')


