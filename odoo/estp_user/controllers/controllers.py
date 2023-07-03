# -*- coding: utf-8 -*-
from odoo import http

# class EstpUser(http.Controller):
#     @http.route('/estp_user/estp_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/estp_user/estp_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('estp_user.listing', {
#             'root': '/estp_user/estp_user',
#             'objects': http.request.env['estp_user.estp_user'].search([]),
#         })

#     @http.route('/estp_user/estp_user/objects/<model("estp_user.estp_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('estp_user.object', {
#             'object': obj
#         })