from odoo import fields, models,api,_
from datetime import date
from odoo.exceptions import ValidationError, UserError
class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Reservation'

    name = fields.Char(string='Reservation Name',compute='_compute_reservation_name',readonly=True,default='')
    check_in = fields.Date(string='Date Check-in',required=True)
    check_out = fields.Date(string='Date Check-out',required=True)
    duration = fields.Integer(string='Reservation Duration',compute='_compute_duration',readonly=True,default=0)
    state = fields.Selection([
        ('reserved', 'Reserved'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='reserved', required=True,store=True)
    partner_id = fields.Many2one('res.partner', string='Customer',required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True)
    room_price = fields.Float(string='Room Price',related='room_id.price', readonly=True)
    reservation_line_ids = fields.One2many('hotel.reservation.line', 'reservation_id', string='Reservation Lines')
    total_price = fields.Float(compute='_compute_total_price', string='Total Price',readonly=True,store=True)

    guests = fields.Integer(string='Guest',default=1)

    _sql_constraints = [
        ('check_valid_dates','CHECK(check_out > check_in)','The check-out date must be later than the check-in date!'),
    ]

    @api.constrains('check_in', 'check_out', 'room_id')
    def _check_reservation_dates(self):
        for reservation in self:
            overlapping_reservations = self.search([
                ('room_id', '=', reservation.room_id.id),
                ('id', '!=', reservation.id),
                ('state', 'not in', ['cancelled']),
                ('check_in', '<', reservation.check_out),
                ('check_out', '>', reservation.check_in),
            ], limit=1)

            if overlapping_reservations:
                raise ValidationError(_("Room %s is already reserved from %s to %s") % (
                                          reservation.room_id.name,
                                          overlapping_reservations.check_in,
                                          overlapping_reservations.check_out
                                      ))


    @api.depends('partner_id')
    def _compute_reservation_name(self):
        for reservation in self:
            if reservation and reservation.partner_id:
                reservation.name = 'Reservation in the name of' + ' ' + reservation.partner_id.name

    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for reservation in self:
            if reservation.check_in and reservation.check_out:
                reservation.duration = (reservation.check_out - reservation.check_in).days
            else:
                reservation.duration = 0

    @api.depends('reservation_line_ids.total_price','room_price')
    def _compute_total_price(self):
        for reservation in self:
            reservation.total_price = reservation.room_price +  sum(reservation.reservation_line_ids.mapped('total_price'))

    @api.onchange('check_in')
    def _onchange_check_in(self):
        if self.check_in and self.check_in < date.today():
            self.check_in = date.today()
            return {
                'warning': {
                    'title': "Date invalide",
                    'message': "The check-in date cannot be earlier than today."
                }
            }

    @api.onchange('check_out', 'check_in')
    def _onchange_check_out(self):
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            return {
                'warning': {
                    'title': "Date invalide",
                    'message': "The check-out date must be strictly later than the check-in date."
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._has_overlapping_reservation(vals.get('room_id'),vals.get('check_in'),vals.get('check_out')):
                raise UserError(_("The room is already reserved during this period"))
        reservations = super(HotelReservation, self).create(vals_list)
        rooms = reservations.mapped('room_id')
        rooms.write({'state': 'reserved'})
        return reservations



    def action_check_in(self):
        self.ensure_one()
        self.state = 'checked_in'
        room = self.env['hotel.room'].sudo().browse(int(self.room_id.id)) if self.room_id.id else None
        room.write({'state': 'occupied'})

    def action_check_out(self):
        self.ensure_one()
        self.state = 'checked_out'
        room = self.env['hotel.room'].sudo().browse(int(self.room_id.id)) if self.room_id.id else None
        room.write({'state': 'available'})

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        room = self.env['hotel.room'].sudo().browse(int(self.room_id.id)) if self.room_id.id else None
        room.write({'state': 'available'})

    def _has_overlapping_reservation(self, room_id, check_in, check_out, exclude_reservation=None):
        domain = [
            ('room_id', '=', room_id),
            ('state', 'not in', ['cancelled']),
            ('check_in', '<', check_out),
            ('check_out', '>', check_in),
        ]
        if exclude_reservation:
            domain.append(('id', '!=', exclude_reservation))
        return bool(self.search_count(domain))

    def write(self, vals):
        if 'check_in' in vals or 'check_out' in vals:
            check_in = vals.get('check_in', self.check_in)
            check_out = vals.get('check_out', self.check_out)
            if check_out <= check_in:
                raise UserError(_("Invalid dates - Duration must be at least 1 day"))

            if self._has_overlapping_reservation(
                    vals.get('room_id', self.room_id.id),
                    check_in,
                    check_out,
                    exclude_reservation=self.id
            ):
                raise UserError(_("The room is already Reserved during this period"))

        return super().write(vals)
