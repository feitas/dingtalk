# -*- coding: utf-8 -*-

import logging
import urllib2
import json

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class DingDepartment(models.Model):
    _inherit = "hr.department"

    ding_id = fields.Integer("钉钉ID")
    dingtalk_create_deptgroup = fields.Boolean("同步创建企业群")
    dingtalk_auto_adduser = fields.Boolean("新人自动入群")
    dt_order = fields.Integer("父部门次序")
    dt_deptHiding = fields.Boolean("隐藏部门")


    @api.multi
    def dingtalk_get_department_details(self):
        for record in self:
            if not record.ding_id:
                continue
            
            token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')
            if not token:
                break
            
            url = "https://oapi.dingtalk.com/department/get?access_token={0}&id={1}".format(token, record.ding_id)

            open = urllib2.urlopen(url)

            result = json.loads(open.read().decode("utf-8"))

            _logger.info(result)

            if result.get('errmsg') == 'ok':
                record.dt_order = result['order']
                record.dt_deptHiding = result['deptHiding']
                record.dingtalk_auto_adduser = result['autoAddUser']
                record.dingtalk_create_deptgroup = result['createDeptGroup']



class DingEmployee(models.Model):
    _inherit = "hr.employee"

    userid = fields.Char("钉钉唯一标识")
    deviceId = fields.Char("设备ID")
    ash_type = fields.Selection([('waterboth', '送水派接'),
    	('waterassign', '送水仅派'),
    	('waterreceive', '送水仅接'),
		('carboth', '车管派接'),
		('carassign', '车管仅派'),
		('carreceive', '车管仅接'),
    	], string="业务类型")