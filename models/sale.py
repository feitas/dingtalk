# -*- coding: utf-8 -*-

import logging
import json
import urllib2

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

# TODO：这些功能应该转移！！！！！！

class dingtalkSale(models.Model):
    _inherit = "sale.order"

    """
    重写create方法，car类型的订单创建时给钉钉发消息
    """
    @api.model
    def create(self, vals):
        sale_order = super(dingtalkSale, self).create(vals)
        # 爱车管家为后付费，所以下单即发送消息
        if sale_order.ash_type == "car":
            target_employee_ids = ""
            # 获得发消息的部门
            departments = self.env['hr.department'].search([('monitor_sale','=',True)])
            department_ids = [depart.id for depart in departments]
            if not departments:
                return sale_order
            # 获得发消息的员工
            employees = self.env['hr.employee'].search([('userid','!=',False),('department_id','in',department_ids)])
            if not employees:
                return sale_order

            target_employee_ids = employees[0].userid
            for employee in employees[1:]:
                target_employee_ids = target_employee_ids + "|" + employee.userid

            # 发送消息
            dingtalkAccount = self.env['dingtalk.account'].search([])
            if not dingtalkAccount:
                return sale_order

            # 获得微应用
            dingtalkApp = self.env['dingtalk.app'].search([('send_enterprise_message','=',True)])
            if not dingtalkApp:
                return sale_order

            # 组装消息内容
            ctuple = (
                sale_order.name,
                sale_order.partner_id.name,
                sale_order.partner_id.mobile,
                sale_order.order_line[0].product_id.name,
                sale_order.order_line[0].name,
                int(sale_order.order_line[0].product_uom_qty),
                sale_order.partner_id.community_id.name,
                sale_order.partner_id.street,
                sale_order.book_start_time,
                sale_order.note
            )
            content = "新订单：%s，业主：%s，电话：%s，项目：%s，说明：%s, 数量：%d，地址：%s，%s。请尽快处理！预约时间：%s, 备注: %s" % ctuple

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

        return sale_order

    """
    重写write方法，water类型的订单付款后给钉钉发消息
    """
    @api.multi
    def write(self, vals):
        sale_order = super(dingtalkSale, self).write(vals)
        _logger.info("钉钉发消息：重写write，定位多次发送问题所在")
        _logger.info(vals)
        for so in self:
            if so.ash_type == "water" and so.state == "sale" and vals.get('state') and vals['state'] == 'sale':
                target_employee_ids = ""
                # 获得发消息的部门
                departments = self.env['hr.department'].search([('monitor_sale', '=', True)])
                department_ids = [depart.id for depart in departments]
                _logger.info(department_ids)
                if not departments:
                    return sale_order
                # 获得发消息的员工
                employees = self.env['hr.employee'].search(
                    [('userid', '!=', False), ('department_id', 'in', department_ids)])
                _logger.info(employees)
                if not employees:
                    return sale_order

                target_employee_ids = employees[0].userid
                for employee in employees[1:]:
                    target_employee_ids = target_employee_ids + "|" + employee.userid

                _logger.info(target_employee_ids)
                # 发送消息
                dingtalkAccount = self.env['dingtalk.account'].search([])
                if not dingtalkAccount:
                    return sale_order

                # 获得微应用
                dingtalkApp = self.env['dingtalk.app'].search([('send_enterprise_message', '=', True)])
                if not dingtalkApp:
                    return sale_order

                # 组装消息内容
                ctuple = (
                    so.name,
                    so.partner_id.name,
                    so.partner_id.mobile,
                    so.order_line[0].product_id.name,
                    int(so.order_line[0].product_uom_qty),
                    so.partner_id.community_id.name,
                    so.partner_id.street
                )
                content = "新订单：%s，业主：%s，电话：%s，项目：%s，数量：%d，地址：%s，%s：，请尽快处理！" % ctuple

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

            return sale_order
