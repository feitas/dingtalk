# -*- coding: utf-8 -*-
from openerp import http

# class AshDingtalk(http.Controller):
#     @http.route('/ash_dingtalk/ash_dingtalk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ash_dingtalk/ash_dingtalk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ash_dingtalk.listing', {
#             'root': '/ash_dingtalk/ash_dingtalk',
#             'objects': http.request.env['ash_dingtalk.ash_dingtalk'].search([]),
#         })

#     @http.route('/ash_dingtalk/ash_dingtalk/objects/<model("ash_dingtalk.ash_dingtalk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ash_dingtalk.object', {
#             'object': obj
#         })