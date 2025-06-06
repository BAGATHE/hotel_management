from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class HotelReservationLine(models.Model):
    _name = 'hotel.reservation.line'
    _description = 'Hotel Reservation Line'

    reservation_id = fields.Many2one('hotel.reservation', string='Reservation', required=True)
    equipment_id = fields.Many2one('hotel.equipment', string='Equipment', required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    unit_price = fields.Float(string='Unit Price', required=True, compute='_compute_unit_price', store=True,default=1)
    total_price = fields.Float(string='Total', compute='_compute_total_price', store=True, readonly=True)

    _sql_constraints = [
        (
            'check_positive_quantity',
            'CHECK(quantity > 0)',
            'Quantity must be greater than zero!'
        ),
        (
            'check_positive_unit_price',
            'CHECK(unit_price >= 0)',
            'The unit price cannot be negative!'
        )
    ]

    @api.depends('equipment_id')
    def _compute_unit_price(self):
        for line in self:
            if line.equipment_id:
                line.unit_price = line.equipment_id.default_price
            else:
                line.unit_price = 0

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.unit_price

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity <= 0:
            self.quantity = 1
            return {
                'warning': {
                    'title': _("Incorrect value"),
                    'message': _("The quantity was reset to 1 because it cannot be less than or equal to 0."),
                }
            }

    @api.constrains('equipment_id', 'reservation_id')
    def _check_equipment_uniqueness(self):
        for line in self:
            if self.search_count([
                ('id', '!=', line.id),
                ('reservation_id', '=', line.reservation_id.id),
                ('equipment_id', '=', line.equipment_id.id)
            ]) > 0:
                raise ValidationError(
                    _("Equipment %s is already present in this reservation.") % line.equipment_id.name
                )