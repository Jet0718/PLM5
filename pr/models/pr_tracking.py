from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class Tracking(models.Model):
    _name = "pr.tracking"
    _description = "PR management of Tracking."
    _inherit = ['mail.thread','mail.activity.mixin']

    lc_po_no =fields.Char(string="批號")  
    lc_verify =fields.Selection(
        string="確認結果",
        selection=[('允收','允收'),('拒收','拒收')]
    )
    date_on =fields.Date("時間" ,copy=False ,default=lambda self: fields.Datetime.today())
    pr_id =fields.Many2one('pr',string="PR問題單")


    _rec_name = 'lc_po_no'   