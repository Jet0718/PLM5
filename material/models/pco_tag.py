from odoo import api,fields, models
from datetime import timedelta

class requirement_purpose(models.Model):
    _name = "pco.tag"
    _description = "tag model for pco. "
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name =fields.Char("標簽名稱",required=True)
    description = fields.Char("標簽說明")