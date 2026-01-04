from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class PartClass(models.Model):
    _name = "part.class"
    _description = "Material management main model of part_class."
    _inherit = ['mail.thread','mail.activity.mixin']
    
    classification =fields.Selection(
        string="分類",
        selection=[('商品存貨','商品存貨'),('成品','成品'),('雷射模組','雷射模組'),
                   ('PCBA','PCBA'),('原物料_LD_LED','原物料_LD_LED'),('原料','原料'),
                   ('模具品','模具品'),('A_需列管','A_需列管'),('B_不需列管','B_不需列管')],
        readonly=False
    )
    name =fields.Char(string="名稱")
    list_id =fields.Many2one('part.list',string="清單選項", domain="[('classification', '=', classification),('name', '=', name)]", create=False ,readonly=False)
    description =fields.Char(string="描述")
    part_id =fields.Many2one('product.template',string="關聯物料")

    _rec_name = 'name' 