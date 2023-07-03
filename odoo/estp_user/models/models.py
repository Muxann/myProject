# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('login')
    def _check_login(self):
        for user in self:
            if not re.match(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", user.login):
                error_message = """Значение поля "Адрес эл. почты (логин)"" должно соответствовать формату: 'username@example.com'"""
                raise ValidationError(error_message)
                

