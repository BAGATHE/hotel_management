# -*- coding: utf-8 -*-
# from odoo import http


# class EtechAddons/hotelProject/hotel(http.Controller):
#     @http.route('/etech_addons/hotel_project/hotel/etech_addons/hotel_project/hotel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etech_addons/hotel_project/hotel/etech_addons/hotel_project/hotel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('etech_addons/hotel_project/hotel.listing', {
#             'root': '/etech_addons/hotel_project/hotel/etech_addons/hotel_project/hotel',
#             'objects': http.request.env['etech_addons/hotel_project/hotel.etech_addons/hotel_project/hotel'].search([]),
#         })

#     @http.route('/etech_addons/hotel_project/hotel/etech_addons/hotel_project/hotel/objects/<model("etech_addons/hotel_project/hotel.etech_addons/hotel_project/hotel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etech_addons/hotel_project/hotel.object', {
#             'object': obj
#         })

