# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

import json
import requests
import time
import hmac
import hashlib
import urllib2

from odoo import api, fields, models


_logger = logging.getLogger(__name__)
_DEPARTMENT_LIST = "https://oapi.dingtalk.com/department/list?access_token={0}"


class DingtalkConfiguration(models.TransientModel):
    _name = 'dingtalk.config.settings'
    _inherit = 'res.config.settings'

    corpID = fields.Char("CorpID", 
        default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpID'))
    corpSecret = fields.Char("CorpSecret", 
        default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpSecret'))
    accessToken = fields.Char("AccessToken", 
        default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken'))
    jsapiTicket = fields.Char("JsapiTicket", 
        default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_jsapiTicket'))


    @api.multi
    def set_corpID_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'dingtalk.config.settings', 'dingtalk_corpID', self.corpID)

    @api.multi
    def set_corpSecret_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'dingtalk.config.settings', 'dingtalk_corpSecret', self.corpSecret)

    @api.multi
    def set_accessToken_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'dingtalk.config.settings', 'dingtalk_accessToken', self.accessToken)

    @api.multi
    def set_jsapiTicket_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'dingtalk.config.settings', 'dingtalk_jsapiTicket', self.jsapiTicket)


    @api.multi
    def get_department_list(self):
        access_token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
        if not access_token:
            return

        department_env = self.env['hr.department']

        url = _DEPARTMENT_LIST.format(access_token)
        open = urllib2.urlopen(url)
        result = json.loads(open.read().decode("utf-8"))

        _logger.info(result)

        if result['errcode'] == 0 and result['errmsg'] == 'ok':
            departments = result['department']
            depart_dic = {}

            for dep in departments:
                depart_dic[dep['id']] = dep

            _logger.info(depart_dic)           

            for depart in departments:
                depart_sequence = [depart['id']]  # 初始化当前的部门id
                parent = depart.get('parentid')  # id=1的部门没有parentid这个key
                
                while parent > 1:
                    parent_search = department_env.search([('ding_id', '=', parent)])
                    # 如果已经存在上级
                    if len(parent_search) == 1:
                        break
                    elif len(parent_search) == 0:
                        # 该上级需要创建，所以将id加进去
                        depart_sequence.append(parent)
                        # 新的parent
                        parent = depart_dic[parent]['parentid']

                # 对要创建的部门排序
                depart_sequence.sort()

                for ds in depart_sequence:
                    ds = depart_dic[ds]

                    _parentid = ds.get('parentid')

                    if _parentid:
                        _parent = department_env.search([('ding_id', '=', _parentid)])

                    _current = department_env.search([('name', '=', ds['name'])])

                    if len(_current) < 1:
                        _create_value = {
                            "name": ds['name'],
                            "ding_id": ds['id']
                        }
                        if _parentid:
                            _create_value['parent_id'] = _parent.id

                        department_env.create(_create_value)
                    elif len(_current) == 1:
                        _current.ding_id = ds['id']
                        if _parentid:
                            _current.parent_id = _parent.id




