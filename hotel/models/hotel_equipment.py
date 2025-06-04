from odoo import fields, models

class HotelEquipment(models.Model):
    _name = 'hotel.equipment'
    _description = 'Hotel Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    description = fields.Char(string='Description')
    default_price = fields.Float(string='Default Price', required=True,default=0)