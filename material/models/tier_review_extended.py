# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TierReviewExtended(models.Model):
    """Extend tier.review model to automatically create/update material.todo records"""
    _inherit = 'tier.review'
    
    # 覆寫 create 方法，在創建審核記錄時自動建立待辦事項
    @api.model_create_multi
    def create(self, vals_list):
        # 先創建審核記錄
        reviews = super().create(vals_list)
        
        # 為每個新創建的審核記錄建立待辦事項
        for review in reviews:
            # 為所有狀態的審核創建待辦事項，但根據狀態設置適當的待辦事項狀態
            self._create_todo_from_review(review)
        
        return reviews
    
    # 覆寫 write 方法，在狀態變化時更新待辦事項
    def write(self, vals):
        # 記錄狀態變化前的狀態
        status_changed = 'status' in vals
        
        # 先執行寫入操作
        result = super().write(vals)
        
        # 如果狀態發生變化，更新對應的待辦事項
        if status_changed:
            for review in self:
                self._update_todo_from_review(review)
        
        return result
    
    def _create_todo_from_review(self, review):
        """從審核記錄建立待辦事項"""
        # 檢查 material.todo 模型是否可用
        if 'material.todo' not in self.env:
            return
        
        # 檢查是否已存在相同 review 的待辦事項
        existing_todo = self.env['material.todo'].search([
            ('review_id', '=', review.id)
        ])
        
        if existing_todo:
            # 如果已存在，更新狀態
            todo_state = self._get_todo_state_from_review_status(review.status)
            existing_todo.write({'state': todo_state})
            return existing_todo
        
        # 為每個 reviewer 建立待辦事項
        todos = self.env['material.todo']
        for reviewer in review.reviewer_ids:
            todo_vals = {
                'name': f"{review.name or '審核'} - {reviewer.name}",
                'model_name': review.model,
                'res_id': review.res_id,
                'user_id': reviewer.id,
                'review_id': review.id,
                'description': self._get_todo_description(review),
                'priority': self._get_todo_priority(review),
                'state': self._get_todo_state_from_review_status(review.status),
            }
            todo = self.env['material.todo'].create(todo_vals)
            todos += todo
        
        return todos
    
    def _update_todo_from_review(self, review):
        """根據審核記錄狀態更新待辦事項"""
        if 'material.todo' not in self.env:
            return
        
        # 查找與此審核相關的所有待辦事項
        todos = self.env['material.todo'].search([
            ('review_id', '=', review.id)
        ])
        
        if not todos:
            # 如果沒有待辦事項，嘗試創建（適用於所有狀態）
            return self._create_todo_from_review(review)
        
        # 根據審核狀態更新待辦事項狀態
        todo_state = self._get_todo_state_from_review_status(review.status)
        
        # 準備更新值
        update_vals = {'state': todo_state}
        
        # 如果審核被批准或拒絕，設置完成時間
        if review.status in ('approved', 'rejected'):
            update_vals['date_done'] = fields.Datetime.now()
        
        # 如果審核狀態變為 pending，設置開始時間
        if review.status == 'pending' and todos[0].state != 'in_progress':
            update_vals['date_start'] = fields.Datetime.now()
        
        # 更新待辦事項
        todos.write(update_vals)
        
        return todos
    
    def _get_todo_state_from_review_status(self, review_status):
        """將審核狀態映射到待辦事項狀態"""
        mapping = {
            'waiting': 'pending',      # 等待中 -> 待處理
            'pending': 'in_progress',  # 待審核 -> 進行中
            'approved': 'done',        # 已批准 -> 已完成
            'rejected': 'cancelled',   # 已拒絕 -> 已取消
        }
        return mapping.get(review_status, 'pending')
    
    def _get_todo_description(self, review):
        """生成待辦事項描述"""
        description_parts = []
        
        if review.name:
            description_parts.append(f"簽核事項: {review.name}")
        
        if review.model and review.res_id:
            try:
                record = self.env[review.model].browse(review.res_id)
                if record.exists():
                    description_parts.append(f"表單: {record.display_name or record.name_get()[0][1]}")
                else:
                    description_parts.append(f"表單: {review.model} ({review.res_id})")
            except Exception:
                description_parts.append(f"表單: {review.model} ({review.res_id})")
        
        if review.definition_id and review.definition_id.name:
            description_parts.append(f"審核定義: {review.definition_id.name}")
        
        return "\n".join(description_parts)
    
    def _get_todo_priority(self, review):
        """根據審核定義決定待辦事項優先級"""
        # 在 Odoo 19 的 tier.definition 中沒有 priority 字段
        # 可以根據其他邏輯決定優先級，例如：
        # 1. 如果有 approve_sequence，可能是較高優先級
        # 2. 或者根據審核類型決定
        # 目前先返回默認值 '1' (中)
        return '1'  # 默認為中
    
    # 當審核記錄被刪除時，刪除對應的待辦事項
    def unlink(self):
        # 先查找並刪除相關的待辦事項
        if 'material.todo' in self.env:
            for review in self:
                todos = self.env['material.todo'].search([
                    ('review_id', '=', review.id)
                ])
                if todos:
                    todos.unlink()
        
        # 然後刪除審核記錄
        return super().unlink()