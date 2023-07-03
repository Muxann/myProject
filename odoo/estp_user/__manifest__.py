# -*- coding: utf-8 -*-
{
    'name': "estp_user",

    'summary': """
       Модуль модифицирует таблицу users""",

    'description': """
        Этот модуль модифицирует карточку пользователя
    """,

    'author': "Maksimchenko Mikhail",
    'website': "http://www.yourcompany.com",
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base'],

    # always loaded
    'data': [
        #'security/security.xml',
        'views/res_users_views.xml',
	    'i18n/ru_RU.po',
    ],

}
