from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class PartList(models.Model):
    _name = "part.list"
    _description = "Material management main model of part_list."
    _inherit = ['mail.thread','mail.activity.mixin']
    
    classification =fields.Selection(
        string="分類",
        selection=[('商品存貨','商品存貨'),('成品','成品'),('雷射模組','雷射模組'),
                   ('PCBA','PCBA'),('原物料_LD_LED','原物料_LD_LED'),('原料','原料'),
                   ('模具品','模具品'),('A_需列管','A_需列管'),('B_不需列管','B_不需列管')],
        readonly=False,required=True
    )
    name =fields.Char(string="名稱",required=True)
    label =fields.Char(string="標籤",required=True)
    value =fields.Char(string="值",required=True)

    _rec_name = 'label' 