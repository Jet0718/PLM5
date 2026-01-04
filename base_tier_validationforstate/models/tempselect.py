from odoo import models, fields, api,_
from datetime import datetime, timedelta

# models.TransientModel是零时数据，定期清理一帮7天左右

class TempselectModel(models.TransientModel):
    _name = "cn.tempselect"
    _description="tempselect"

    cn_controlid = fields.Integer("control id")
    res_type =fields.Char("type")
    sequence = fields.Integer("sequence")

    
    # 多选结果的记录（many2many字段）
    selected_records = fields.Many2many(
        'tier.definition',  # 替换为你的目标模型（如product.product）
        string="选择记录",
        
    )
    def action_on_close(self):
       domain = []
      
       selected_records =self.selected_records
       if len(selected_records)>0:        
           cn_controlid =self.cn_controlid
        #    domain.append(("model", "=", self.res_type))
           domain.append(("id", "=", cn_controlid))
           col_item = self.env[self.res_type].search(domain)
           
           for nd in selected_records:   
            reviewitem=self.env['tier.review'].search([('definition_id','=',nd.id),('id','in',col_item.review_ids.ids)])
            reviewitem =reviewitem[len(reviewitem)-1]
            if col_item.has_comment:
                    return col_item._add_comment("reject", reviewitem)
            col_item._rejected_tier(reviewitem)
            col_item._update_counter({"review_deleted": True})
           
    def select_row(self):
        v=self
    # def action_search(self):
    #     """根据条件过滤记录"""
    #     domain = []
    #     if self.name_filter:
    #         domain.append(('name', 'ilike', self.name_filter))
    #     if self.date_filter:
    #         domain.append(('date_field', '=', self.date_filter))  # 替换为实际日期字段
        
    #     # 更新多选字段的候选记录
    #     records = self.env['your.target.model'].search(domain)
    #     self.selected_records = records
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': self._name,
    #         'view_mode': 'form',
    #         'res_id': self.id,
    #         'target': 'new',
    #     }

    # def action_confirm(self):
    #     """确认选择，将值传回原表单"""
    #     active_model = self.env.context.get('active_model')
    #     active_id = self.env.context.get('active_id')
    #     if active_model and active_id:
    #         # 获取原记录并更新字段（示例：更新many2many字段）
    #         record = self.env[active_model].browse(active_id)
    #         record.your_many2many_field = self.selected_records
    #     return {'type': 'ir.actions.act_window_close'}

            

