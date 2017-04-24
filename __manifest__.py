# -*- coding: utf-8 -*-
{
    'name': "dingtalk",

    'summary': """
        钉钉接口""",

    'description': """
        1. 钉钉账号管理，自动任务获取AccessToken

        2. 初始化成员，与Partner进行关联

        3. 企业会话消息接口
    """,

    'author': "Feitas",
    'website': "http://malijie.cc",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/hr.xml',
        'views/templates.xml',
        'views/res_config.xml',
        'views/dingtalk_views.xml',
        'views/multi_actions.xml',
        'views/actions.xml',
        'views/menu_actions.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}