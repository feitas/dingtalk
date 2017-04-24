# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import logging
import sys

from odoo import models, fields, api

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)

_ACCESS_URL = "https://oapi.dingtalk.com/gettoken?corpid={0}&corpsecret={1}"
_DEPARTMENT_LIST = "https://oapi.dingtalk.com/department/list?access_token={0}"
_DEPARTMENT_USERLIST = "https://oapi.dingtalk.com/user/simplelist?access_token={0}&department_id={1}"
_DEPARTMENT_USERDETAILLIST = "https://oapi.dingtalk.com/user/list?access_token={0}&department_id={1}"
_ENTERPRISE_CHAT = "https://oapi.dingtalk.com/message/send?access_token={0}"
_JSAPITICKET = "https://oapi.dingtalk.com/get_jsapi_ticket?access_token={0}"

class dingtalkLog(models.Model):
    _name = 'dingtalk.log'

    name = fields.Char()
    errmsg = fields.Char()
    create_date = fields.Datetime()

    @api.model
    def cron_get_access_token(self):
        """
        自动更新AccessToken
        :return:
        """
        corpid = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpID')
        corpsecret = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpSecret')

        if not corpid or not corpsecret:
            self.create({"name":"get accesstoken", "errmsg":"corpID或corpSecret没有设置！"})
        else:
            url = _ACCESS_URL.format(corpid,corpsecret)
            open = urllib2.urlopen(url)
            results = json.loads(open.read().decode("utf-8"))

            if results['errcode'] == 0 and results['errmsg'] == 'ok':
                self.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_accessToken', results['access_token'])
                
                url2 = _JSAPITICKET.format(results['access_token'])
                open2 = urllib2.urlopen(url2)
                results2 = json.loads(open2.read().decode("utf-8"))
                
                if results2['errcode'] == 0 and results2['errmsg'] == 'ok':
                    self.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_jsapiTicket', results2['ticket'])
                else:
                    self.create({"name":"get jsapi ticket", "errmsg":results2['errmsg']})
            else:
                self.create({"name":"get accesstoken", "errmsg":results['errmsg']})






