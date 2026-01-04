from odoo import api,fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError

class PCOBomModel(models.Model):
    _name = "pco.bom"
    _description = "PCO_BOM main model for PCO."
    _inherit = ['mail.thread','mail.activity.mixin']
        
    pco_id_bom =fields.Many2one("pco")
    affected_bom_id =fields.Many2one('mrp.bom',string='審批物料清單') 
    active =fields.Boolean("啟用",default=True)   
    new_affected_bom_id =fields.Many2one('mrp.bom',string='新版物料清單')
    #添加显示版本
    affected_bom_version = fields.Integer('物料清單舊版本',  related='affected_bom_id.version', readonly=True)
    new_affected_bom_version = fields.Integer('物料清單新版本',  related='new_affected_bom_id.version', readonly=True)

    def open_bom_related_record(self):
        self.ensure_one()       
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.bom',  # 可以是任意模型
                'view_mode': 'form',
                'res_id': self.new_affected_bom_id.id,
                'view_id': self.env.ref('material.mrp_bom_inherit_partbom_view_form').id,  # 自定義視圖
                'target': 'new',  # 打開浮層對話框
                
            }
    def open_oldbom_related_record(self):
        self.ensure_one()       
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.bom',  # 可以是任意模型
                'view_mode': 'form',
                'res_id': self.affected_bom_id.id,
                'view_id': self.env.ref('material.mrp_bom_inherit_partbom_view_form').id,  # 自定義視圖
                'target': 'new',  # 打開浮層對話框
                
            }
    