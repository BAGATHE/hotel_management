from odoo import fields, models,api

class HotelEquipment(models.Model):
    _name = 'hotel.equipment'
    _description = 'Hotel Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    description = fields.Char(string='Description')
    default_price = fields.Float(string='Default Price', required=True,default=0)

    _sql_constraints = [
        ('unique_equipment_name', 'UNIQUE(name)', 'name must be unique'),
        ('positive_default_price', 'CHECK(default_price > 0)', 'default_price must be greater than 0'),
    ]

    @api.onchange('default_price')
    def _onchange_default_price(self):
        if self.default_price < 0:
            self.default_price = 0