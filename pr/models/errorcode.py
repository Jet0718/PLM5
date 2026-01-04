from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class ErrorCode(models.Model):
    _name = "errorcode"
    _description = "PR management of ErrorCode."
    _inherit = ['mail.thread','mail.activity.mixin']

    error_code =fields.Char("錯誤代碼代號",required=True)
    error_name =fields.Char("錯誤代碼名稱",required=True)
    display_name =fields.Char(string="Keyname" , compute ='_compute_display_name',store=True)

    @api.depends('error_code', 'error_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.error_code} - {record.error_name}"


    _rec_name = 'display_name'   