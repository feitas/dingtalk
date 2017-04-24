# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import logging
import sys

from openerp import models, fields, api

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)

_ACCESS_URL = "https://oapi.dingtalk.com/gettoken?corpid={0}&corpsecret={1}"
_DEPARTMENT_LIST = "https://oapi.dingtalk.com/department/list?access_token={0}"
_DEPARTMENT_USERLIST = "https://oapi.dingtalk.com/user/simplelist?access_token={0}&department_id={1}"
_DEPARTMENT_USERDETAILLIST = "https://oapi.dingtalk.com/user/list?access_token={0}&department_id={1}"
_ENTERPRISE_CHAT = "https://oapi.dingtalk.com/message/send?access_token={0}"
_JSAPITICKET = "https://oapi.dingtalk.com/get_jsapi_ticket?access_token={0}"

class dingtalkAccount(models.Model):
    _name = 'dingtalk.account'

    name = fields.Char()
    access_token = fields.Char()
    corpid = fields.Char(required=True)
    corpsecret = fields.Char(required=True)
    jsapi_ticket = fields.Char("Jsapi Ticket")
    errmsg = fields.Char()

    @api.model
    def cron_get_access_token(self):
        """
        自动更新AccessToken
        :return:
        """
        accounts = self.search([])
        for account in accounts:
            url = _ACCESS_URL.format(account.corpid,account.corpsecret)
            open = urllib2.urlopen(url)
            results = json.loads(open.read().decode("utf-8"))

            if results['errcode'] == 0 and results['errmsg'] == 'ok':
                account.write({"access_token":results['access_token']})
                url2 = _JSAPITICKET.format(results['access_token'])
                open2 = urllib2.urlopen(url2)
                results2 = json.loads(open2.read().decode("utf-8"))
                if results2['errcode'] == 0 and results2['errmsg'] == 'ok':
                    account.write({"jsapi_ticket": results2['ticket']})
            else:
                account.write({"errmsg":results['errmsg']})

    @api.multi
    def btn_department(self):
        """
        将钉钉中的部门获取到Odoo
        :return:
        """
        department_obj = self.env['hr.department']
        for record in self:
            url = _DEPARTMENT_LIST.format(record.access_token)
            open = urllib2.urlopen(url)
            results = json.loads(open.read().decode("utf-8"))
            _logger.info(results)
            if results['errcode'] == 0 and results['errmsg'] == 'ok':
                departments = results['department']
                for depart in departments:
                    depart_search = department_obj.search([('name','=',depart['name'])])
                    if not depart_search:
                        depart_create = department_obj.create({
                            'name': depart['name'],
                            'ding_id': depart['id']
                        })
                    else:
                        depart_search.write({'ding_id': depart['id']})

    @api.multi
    def btn_department_userlist(self):
        """
        将钉钉中的员工获取到Odoo
        :return:
        """
        employee_obj = self.env['hr.employee']

        for record in self:
            departments = self.env['hr.department'].search([('ding_id','>',0)])
            for depart in departments:
                url = _DEPARTMENT_USERDETAILLIST.format(record.access_token,depart.ding_id)
                open = urllib2.urlopen(url)
                results = json.loads(open.read().decode("utf-8"))

                if results['errcode'] == 0 and results['errmsg'] == 'ok':
                    user_lists = results['userlist']
                    for user in user_lists:
                        employee_search = employee_obj.search([('name','=',user['name'])])
                        _logger.info(user['name'])
                        if not employee_search:
                            create_values = {
                                'name': user['name'],
                                'userid': user['userid'],
                                'department_id': depart.id,
                                'mobile_phone': user['mobile']
                            }
                            employee_create = employee_obj.create(create_values)
                        else:
                            employee_search.write({"mobile_phone": user['mobile'], "department_id": depart.id})

    @api.multi
    def btn_enterprise_chat(self):
        for rec in self:
            message = {
                "touser":"052128434380992076",
                "agentid":"28845096",
                "msgtype":"text",
                "text":{
                    "content":"测试"
                }
            }
            url = _ENTERPRISE_CHAT.format(rec.access_token)
            data = json.dumps(message, ensure_ascii=False).encode("utf-8")
            req = urllib2.Request(url, data)
            req.add_header("Content-Type","application/json")
            response = urllib2.urlopen(req).read()
            results = json.loads(response.decode("utf-8"))
            _logger.info(results)


    @api.model
    def send_message_microapp(self, content=''):
        sale_order = False
        _logger.info("+++++++++++++++++++")
        _logger.info(content)
        target_employee_ids = ""
        # 获得发消息的部门
        departments = self.env['hr.department'].search([('monitor_sale','=',True)])
        department_ids = [depart.id for depart in departments]
        if not departments:
            _logger.info("钉钉发消息：部门出错")
            return sale_order
        # 获得发消息的员工
        employees = self.env['hr.employee'].search([('userid','!=',False),('department_id','in',department_ids)])
        if not employees:
            _logger.info("钉钉发消息：员工出错")
            return sale_order

        target_employee_ids = employees[0].userid
        for employee in employees[1:]:
            target_employee_ids = target_employee_ids + "|" + employee.userid

        # 发送消息
        dingtalkAccount = self.env['dingtalk.account'].search([])
        if not dingtalkAccount:
            _logger.info("钉钉发消息：账号出错")
            return sale_order

        # 获得微应用
        dingtalkApp = self.env['dingtalk.app'].search([('send_enterprise_message','=',True)])
        if not dingtalkApp:
            _logger.info("钉钉发消息：微应用出错")
            return sale_order

        message = {
            "touser": target_employee_ids,
            "agentid": str(dingtalkApp[0].agent_id),
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        url = "https://oapi.dingtalk.com/message/send?access_token={0}".format(dingtalkAccount[0].access_token)
        data = json.dumps(message, ensure_ascii=False).encode("utf-8")
        req = urllib2.Request(url, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req).read()
        results = json.loads(response.decode("utf-8"))

        _logger.info(results)
        


class dingtalkApp(models.Model):
    _name = "dingtalk.app"

    agent_id = fields.Integer("应用ID")
    name = fields.Char("名称")
    send_enterprise_message = fields.Boolean("发送企业消息")






