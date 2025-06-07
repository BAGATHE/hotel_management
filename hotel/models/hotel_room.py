from odoo import fields, models,api

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'

    name = fields.Char(string='Hotel Room Name', required=True)
    description = fields.Text(string='Hotel Room Description')
    base_price = fields.Float(string='Hotel Room Base Price')
    price = fields.Float(string='Hotel Room Price',compute='_compute_price',store=True,readonly=True)
    max_allowed_person = fields.Integer(string='Hotel Room Max Allowed', required=True,default=2)

    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
    ], string="State", default='available', store=True,readonly=True)

    room_type_id = fields.Many2one(
        'hotel.room.type',
        string='Hotel Room Type',
        required=True,
    )
    room_equipment_ids = fields.One2many(
        'hotel.room.equipment',
        'room_id',
        string='Equipments')

    reservation_ids = fields.One2many('hotel.reservation','room_id',string='Reservations')
    active_reservation = fields.Integer(string='Active Reservation', compute='_compute_active_reservation',store=True,readonly=True)

    _sql_constraints = [
        ('check_unique_name', 'unique(name)','name already exists'),
        ('check_base_price','check(base_price > 0)','base_price must be greater than 0'),
        ('check_allowed_person','check(max_allowed_person > 0)','max_allowed_person must be greater than 0'),
    ]


    @api.onchange('base_price')
    def _onchange_base_price(self):
        if self.base_price < 0 :
            self.base_price = 1

    @api.onchange('max_allowed_person')
    def _onchange_max_allowed_person(self):
        if self.max_allowed_person < 0 or self.max_allowed_person > 5:
            self.max_allowed_person = 1


    @api.depends('base_price','room_equipment_ids')
    def _compute_price(self):
        for room in self:
            if room.room_equipment_ids:
                total_equipment = sum(room.room_equipment_ids.equipment_id.mapped('default_price'))
                room.price = room.base_price + total_equipment
            else:
                room.price = room.base_price

    def action_view_reservations(self):
        self.ensure_one()
        return ({
            'type': 'ir.actions.act_window',
            'name': 'Room Reservations',
            'res_model': 'hotel.reservation',
            'view_mode': 'list',
            'view_id': self.env.ref('hotel.view_room_reservations_popup').id,
            'target': 'new',
            'domain': [('room_id', '=', self.id)],
            'context': {
                'default_room_id': self.id,
                'search_default_group_by_customer': 1
            }
        })

    @api.depends('reservation_ids.state')
    def _compute_active_reservation(self):
        for room in self:
            count = 0
            for reservation in room.reservation_ids:
                if reservation.state != 'cancelled' and reservation.state != 'checked_out':
                    count+=1
            room.active_reservation = count