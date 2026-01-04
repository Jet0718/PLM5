from odoo import api,fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError

class PCOProductModel(models.Model):
    _name = "pco.product"
    _description = "PCO_product main model for PCO."
    # _inherit = ['mail.thread','mail.activity.mixin']
        
    pco_id_prd =fields.Many2one("pco")
    affected_product_id =fields.Many2one('product.template',string='審批產品')
    active =fields.Boolean("啟用",default=True)    
    #ebert 
    new_affected_product_id =fields.Many2one('product.template',string='新審批產品')  
    #添加显示版本
    affected_product_version = fields.Integer('產品舊版本',  related='affected_product_id.version', readonly=True)
    new_affected_product_version = fields.Integer('產品新版本',  related='new_affected_product_id.version', readonly=True)

    def open_related_record(self):
        self.ensure_one()       
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',  # 可以是任意模型
                'view_mode': 'form',
                'res_id': self.new_affected_product_id.id,
                'view_id': self.env.ref('material.product_template_inherit_part_view_form').id,  # 自定義視圖
                'target': 'new',  # 打開浮層對話框
                
            }
    def open_old_related_record(self):
        self.ensure_one()       
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',  # 可以是任意模型
                'view_mode': 'form',
                'res_id': self.affected_product_id.id,
                'view_id': self.env.ref('material.product_template_inherit_part_view_form').id,  # 自定義視圖
                'target': 'new',  # 打開浮層對話框
                
            }
