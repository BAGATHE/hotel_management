from odoo import fields, models,api,_

class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Reservation'

    name = fields.Char(string='Reservation Name',compute='_compute_reservation_name',readonly=True)
    check_in = fields.Datetime(string='Date Check-in',required=True)
    check_out = fields.Datetime(string='Date Check-out',required=True)
    duration = fields.Integer(string='Reservation Duration',compute='_compute_duration',readonly=True,default=0)
    state = fields.Selection([
        ('reserved', 'Reserved'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='reserved', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer',required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True)

    _sql_constraints = [
        ('check_valid_dates','CHECK(check_out > check_in)','The check-out date must be later than the check-in date!'),
    ]

    @api.depends('partner_id')
    def _compute_reservation_name(self):
        for reservation in self:
            if reservation.partner_id:
                self.name = 'Reservation in the name of' + ' ' + reservation.partner_id.name

    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for reservation in self:
            if reservation.check_in and reservation.check_out:
                self.duration = (reservation.check_out - reservation.check_in).days
            else:
                self.duration = 0