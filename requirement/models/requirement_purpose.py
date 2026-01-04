from odoo import api,fields, models
from datetime import timedelta

class requirement_purpose(models.Model):
    _name = "requirement.purpose"
    _description = "purpose lib model for require management."
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name =fields.Char("用途名称",required=True)