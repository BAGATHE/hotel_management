from odoo import http
from odoo.http import request
from datetime import date, timedelta, datetime
from odoo.exceptions import UserError


def _parse_reservation_params(checkin, checkout, guests):
    today = date.today()
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date() if checkin else today
    except ValueError:
        raise UserError("invalid date checkin")
    try:
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date() if checkout else today + timedelta(days=1)
    except ValueError:
        raise UserError("invalid date checkout")

    if checkin_date < today:
        raise UserError("The check-in date cannot be earlier than today.")

    if checkout_date <= checkin_date:
        raise UserError("The check-out date must be later than the check-in date.")

    try:
        guests_count = int(guests) if guests else 2
    except ValueError:
        guests_count = 2

    return checkin_date, checkout_date, guests_count



class CustomerController(http.Controller):

    @http.route('/', type='http', auth='user', website=True)
    def hotel_homepage(self, checkin=None, checkout=None, guests=2, **kw):
        HotelRoom = request.env['hotel.room']
        HotelReservation = request.env['hotel.reservation']

        checkin_date,checkout_date,guests = _parse_reservation_params(checkin, checkout, guests)

        if checkin_date >= checkout_date:
            return request.render('hotel_front_office.custom_homepage', {
                'error': "The departure date must be later than the arrival date.",
                'rooms': [],
                'checkin': checkin_date,
                'checkout': checkout_date,
                'guests': guests
            })

        overlapping_reservations = HotelReservation.search([
            ('state', 'in', ['reserved', 'checked_in']),
            ('check_in', '<', checkout_date),
            ('check_out', '>', checkin_date),
        ])

        reserved_room_ids = overlapping_reservations.mapped('room_id.id')

        available_rooms = HotelRoom.search([
            ('id', 'not in', reserved_room_ids),
            ('max_allowed_person', '>=', guests),
        ])

        return request.render('hotel_front_office.custom_homepage', {
            'rooms': available_rooms,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'guests': guests
        })


    @http.route('/hotel/reserve', type='http', auth='user', website=True)
    def reserve_room(self, room_id=None, checkin=None, checkout=None, guests=2, **kw):
        guests = int(guests) if guests else 2
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date() if checkin else date.today()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date() if checkout else checkin_date + timedelta(days=1)

        Room = request.env['hotel.room'].sudo()
        Equipment = request.env['hotel.equipment'].sudo()

        room = Room.browse(int(room_id)) if room_id else None
        room_equipment_ids = room.room_equipment_ids.mapped('equipment_id').ids if room else []

        available_equipments = Equipment.search([('id', 'not in', room_equipment_ids)])

        if not room:
            return request.render('website.404')

        return request.render('hotel_front_office.reservation_form', {
            'room': room,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'guests': guests,
            'equipments': available_equipments,
        })


    @http.route('/hotel/confirm_reservation', type='http', auth='user', methods=['POST'], website=True)
    def confirm_reservation(self, **post):
        room_id = int(post.get('room_id'))
        checkin_str = post.get('checkin')
        checkout_str = post.get('checkout')
        guests = int(post.get('guests', 2))
        equipment_ids = request.httprequest.form.getlist('equipment_ids')

        try:
            checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()
        except Exception:
            return request.render("website.404")

        duration = (checkout - checkin).days
        if duration <= 0:
            return request.render("website.404")

        partner = request.env.user.partner_id

        reservation = request.env['hotel.reservation'].sudo().create({
            'check_in': checkin,
            'check_out': checkout,
            'room_id': room_id,
            'partner_id': partner.id,
            'state': 'reserved',
        })

        for eq_id in equipment_ids:
            request.env['hotel.reservation.line'].sudo().create({
                'reservation_id': reservation.id,
                'equipment_id': int(eq_id),
                'unit_price':1
            })

        return request.redirect('/hotel/reservations')



    @http.route('/hotel/reservations', type='http', auth='user', website=True)
    def user_reservations(self):
        partner = request.env.user.partner_id

        reservations = request.env['hotel.reservation'].sudo().search([
            ('partner_id', '=', partner.id)
        ])

        return request.render('hotel_front_office.user_reservations_template', {
            'reservations': reservations,
            'partner': partner,
        })

    @http.route('/hotel/reservation', type='http', auth='user', website=True)
    def view_reservation_detail(self, reservation_id=None, **kwargs):
        reservation = request.env['hotel.reservation'].sudo().browse(int(reservation_id)) if reservation_id else None
        if not reservation or not reservation.exists():
            return request.not_found()
        return request.render('hotel_front_office.reservation_detail_template', {
            'reservation': reservation,
        })
    @http.route('/hotel/reservation/cancel', type='http', auth='user', website=True)
    def cancel_reservation(self, reservation_id=None, **kwargs):
        reservation = request.env['hotel.reservation'].sudo().browse(int(reservation_id)) if reservation_id else None
        if reservation:
            reservation.write({'state': 'cancelled'})
        return request.redirect('/hotel/reservations')
