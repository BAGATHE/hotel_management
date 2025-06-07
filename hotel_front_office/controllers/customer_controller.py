from odoo import http
from odoo.http import request
from datetime import date, timedelta, datetime
from odoo.exceptions import UserError
from ..utils.response_utils import OdooResponseUtils
import json
from odoo import fields
import traceback

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
            room = request.env['hotel.room'].sudo().browse(int(reservation.room_id.id)) if reservation.room_id.id else None
            if room and room.exists():
                room.write({'state': 'available'})
        return request.redirect('/hotel/reservations')

    @http.route('/hotel/reservation/free', type='http', auth='user', website=True)
    def free_room(self, reservation_id=None, **kwargs):
        reservation = request.env['hotel.reservation'].sudo().browse(int(reservation_id)) if reservation_id else None
        if reservation:
            reservation.write({'state': 'checked_out'})
            room = request.env['hotel.room'].sudo().browse(
                int(reservation.room_id.id)) if reservation.room_id.id else None
            if room and room.exists():
                room.write({'state': 'available'})
        return request.redirect('/hotel/reservations')

    """------------------------CALL APi-----------------------------------------------------------------------------------"""





    @http.route('/api/equipments', auth='public', type='http', methods=['GET'], csrf=False, website=False)
    def api_get_equipments(self, **kw):
        try:
            equipments = request.env['hotel.equipment'].sudo().search([])
            equipment_data = equipments.read(['id', 'name', 'default_price'])
            return request.make_json_response(OdooResponseUtils.success(data=equipment_data))

        except Exception as e:
            return request.make_json_response(
                OdooResponseUtils.error(error=str(e),code=500))

    @http.route('/api/hotel/reservation', type='http', auth='public', methods=['POST'], csrf=False,website=False)
    def api_reservation(self, **post):
        try:
            data = json.loads(request.httprequest.data)

            room_id = data.get('room_id')
            checkin = fields.Date.to_date(data.get('checkin'))
            checkout = fields.Date.to_date(data.get('checkout'))
            guests = data.get('guests', 1)
            partner_id = data.get('partner_id')
            equipment_ids = data.get('equipment_ids', [])

            if (checkout - checkin).days <= 0:
                return request.make_json_response(OdooResponseUtils.error(
                    error='Invalid dates: Check-out must be after check-in',
                    code=400
                ))

            reservation = request.env['hotel.reservation'].sudo().create({
                'check_in': checkin,
                'check_out': checkout,
                'room_id': room_id,
                'partner_id': partner_id,
                'guests': guests,
                'state': 'reserved',
            })

            for eq_id in equipment_ids:
                request.env['hotel.reservation.line'].sudo().create({
                    'reservation_id': reservation.id,
                    'equipment_id': int(eq_id),
                    'unit_price': 1
                })

            return request.make_json_response(OdooResponseUtils.success(
                data={
                    'reservation_id': reservation.id,
                    'confirmation_number': reservation.name,
                    'total_amount': reservation.total_price
                },
                code=201,
                message='Reservation created successfully'
            ))

        except ValueError as e:
            return request.make_json_response(OdooResponseUtils.error(
                error='Invalid data format',
                error_details=str(e),
                code=400
            ))

        except Exception as e:

            traceback.print_exc()
            return request.make_json_response(OdooResponseUtils.error(
                error='Reservation failed',
                error_details=str(e),
                code=500
            ))

    @http.route('/api/hotel/rooms', type='http', auth='public', methods=['GET'], csrf=False, website=False)
    def api_available_room(self, **kw):
            try:
                data = json.loads(request.httprequest.data)

                checkin = fields.Date.to_date(data.get('checkin'))
                checkout = fields.Date.to_date(data.get('checkout'))
                guests = data.get('guests', 2)

                if (checkout - checkin).days <= 0:
                    return request.make_json_response(OdooResponseUtils.error(
                        error='Invalid dates: Check-out must be after check-in',
                        code=400
                    ))

                overlapping_res = request.env['hotel.reservation'].sudo().search([
                    ('state', 'not in', ['cancelled']),
                    ('check_in', '<=', checkout),
                    ('check_out', '>=', checkin),
                ]).mapped('room_id.id')

                rooms = request.env['hotel.room'].sudo().search([('id', 'not in', overlapping_res),('max_allowed_person', '>=', guests)])
                room_data = rooms.read([])
                return request.make_json_response(OdooResponseUtils.success(data=room_data))

            except ValueError as e:
                return request.make_json_response(OdooResponseUtils.error(
                    error='Invalid data format',
                    error_details=str(e),
                    code=400
                ))

            except Exception as e:

                traceback.print_exc()
                return request.make_json_response(OdooResponseUtils.error(
                    error='check room failed',
                    error_details=str(e),
                    code=500
                ))

    @http.route('/api/reservations', auth='public', type='http', methods=['GET'], csrf=False, website=False)
    def api_get_reservation(self, **kw):
        try:
            reservations = request.env['hotel.reservation'].sudo().search([])
            reservation_data = reservations.read(['id', 'name', 'state'])
            return request.make_json_response(OdooResponseUtils.success(data=reservation_data))

        except Exception as e:
            return request.make_json_response(
                OdooResponseUtils.error(error=str(e), code=500))


    @http.route('/api/hotel/reservation/free', type='http', auth='public', methods=['GET'], csrf=False, website=False)
    def api_free_room(self, **kw):
        data = json.loads(request.httprequest.data)
        reservation_id = data.get('reservation_id')

        reservation = request.env['hotel.reservation'].sudo().browse(int(reservation_id)) if reservation_id else None
        if reservation:
            reservation.write({'state': 'checked_out'})
            room = request.env['hotel.room'].sudo().browse(
                int(reservation.room_id.id)) if reservation.room_id.id else None
            if room and room.exists():
                room.write({'state': 'available'})
        return request.make_json_response(OdooResponseUtils.success(message='room free successfully'))