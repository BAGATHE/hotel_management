# -*- coding: utf-8 -*-
# from odoo import http


# class EtechAddons/hotelProject/hotelFrontOffice(http.Controller):
#     @http.route('/etech_addons/hotel_project/hotel_front_office/etech_addons/hotel_project/hotel_front_office', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/etech_addons/hotel_project/hotel_front_office/etech_addons/hotel_project/hotel_front_office/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('etech_addons/hotel_project/hotel_front_office.listing', {
#             'root': '/etech_addons/hotel_project/hotel_front_office/etech_addons/hotel_project/hotel_front_office',
#             'objects': http.request.env['etech_addons/hotel_project/hotel_front_office.etech_addons/hotel_project/hotel_front_office'].search([]),
#         })

#     @http.route('/etech_addons/hotel_project/hotel_front_office/etech_addons/hotel_project/hotel_front_office/objects/<model("etech_addons/hotel_project/hotel_front_office.etech_addons/hotel_project/hotel_front_office"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('etech_addons/hotel_project/hotel_front_office.object', {
#             'object': obj
#         })

