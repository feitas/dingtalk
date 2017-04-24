# -*- coding: utf-8 -*-

import logging
import urllib2
import json

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class DingDepartment(models.Model):
    _inherit = "hr.department"

    ding_id = fields.Integer("钉钉ID", readonly=True)
    dingtalk_create_deptgroup = fields.Boolean("同步创建企业群")
    dingtalk_auto_adduser = fields.Boolean("新人自动入群")
    dt_order = fields.Integer("父部门次序")
    dt_deptHiding = fields.Boolean("隐藏部门")


    @api.multi
    def dingtalk_get_department_details(self):
        """获取部门详情"""
        token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
        if not token:
            return

        for record in self:
            if not record.ding_id:
                continue
            
            url = "https://oapi.dingtalk.com/department/get?access_token={0}&id={1}".format(token, record.ding_id)

            open = urllib2.urlopen(url)

            result = json.loads(open.read().decode("utf-8"))

            _logger.info(result)

            if result.get('errmsg') == 'ok':
                record.dt_order = result['order']
                record.dt_deptHiding = result['deptHiding']
                record.dingtalk_auto_adduser = result['autoAddUser']
                record.dingtalk_create_deptgroup = result['createDeptGroup']


    @api.multi
    def dingtalk_update_department(self):
        """创建或者更新部门"""
        token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
        if not token:
            return
        
        for record in self:
            # 不允许无父部门
            if not record.parent_id or not record.parent_id.ding_id:
                continue

            if record.ding_id:
                param = {
                    "name": record.name,
                    "parentid": record.parent_id.ding_id,
                    "deptHiding": record.dt_deptHiding
                }

                url = "https://oapi.dingtalk.com/department/update?access_token={0}".format(token)
                data = json.dumps(param, ensure_ascii=False).encode("utf-8")
                req = urllib2.Request(url, data)
                req.add_header("Content-Type", "application/json")
                response = urllib2.urlopen(req).read()
                result = json.loads(response.decode("utf-8"))

                _logger.info(result)
                if result.get('errcode') == 0 and result.get('errmsg') in ['ok','updated']:
                    _logger.info("department updated!")

            else:

                param = {
                    "name": record.name,
                    "parentid": record.parent_id.ding_id
                }

                url = "https://oapi.dingtalk.com/department/create?access_token={0}".format(token)
                data = json.dumps(param, ensure_ascii=False).encode("utf-8")
                req = urllib2.Request(url, data)
                req.add_header("Content-Type", "application/json")
                response = urllib2.urlopen(req).read()
                result = json.loads(response.decode("utf-8"))

                _logger.info(result)
                if result.get('errcode') == 0 and result.get('errmsg') in ['ok','created']:
                    record.ding_id = result['id']



    @api.multi
    def dingtalk_get_deptuser_detail(self):
        """获取部门成员详情， GET"""
        token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
        if not token:
            return

        for record in self:
            if not record.ding_id:
                continue

            url = "https://oapi.dingtalk.com/user/list?access_token={0}&department_id={1}".format(token, record.ding_id)

            has_more = True

            while has_more:
                open = urllib2.urlopen(url)

                result = json.loads(open.read().decode("utf-8"))
                _logger.info(result)
                has_more = result.get('hasMore')

                userlist = result['userlist']
                for user in userlist:
                    employee = self.env['hr.employee'].search([('name', '=', user['name'])])
                    if len(employee) == 0:
                        _createvalue = {
                            "name": user['name'],
                            "userid": user['userid'],
                            "isAdmin": user['isAdmin']
                        }

                        self.env['hr.employee'].create(_createvalue)




class DingEmployee(models.Model):
    _inherit = "hr.employee"

    userid = fields.Char("钉钉唯一标识")
    deviceId = fields.Char("设备ID")
    isAdmin = fields.Boolean("是管理员")
    isBoss = fields.Boolean("是老板")
    isHide = fields.Boolean("隐藏")
    isLeader = fields.Boolean("是Leader")


    @api.multi
    def dingtalk_create_employee(self):
        """创建成员， POST"""

        token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
        if not token:
            return

        for record in self:
            if not record.userid and record.mobile_phone and record.department_id and record.department_id.ding_id:
                param = {
                    "name": record.name,
                    "department": [record.department_id.ding_id],
                    "mobile": record.mobile_phone
                }


                url = "https://oapi.dingtalk.com/user/create?access_token={0}".format(token)
                data = json.dumps(param, ensure_ascii=False).encode("utf-8")
                req = urllib2.Request(url, data)
                req.add_header("Content-Type", "application/json")
                response = urllib2.urlopen(req).read()
                result = json.loads(response.decode("utf-8"))

                _logger.info(result)
                if result.get('errcode') == 0 and result.get('errmsg') in ['ok','created']:
                    record.userid = result['userid']

            elif record.userid and record.name:
                param = {
                    "name": record.name,
                    "userid": record.userid,
                }


                url = "https://oapi.dingtalk.com/user/update?access_token={0}".format(token)
                data = json.dumps(param, ensure_ascii=False).encode("utf-8")
                req = urllib2.Request(url, data)
                req.add_header("Content-Type", "application/json")
                response = urllib2.urlopen(req).read()
                result = json.loads(response.decode("utf-8"))

                _logger.info(result)
                if result.get('errcode') == 0 and result.get('errmsg') in ['ok','updated']:
                    _logger.info("user updated!")






