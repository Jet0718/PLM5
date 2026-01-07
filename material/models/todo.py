# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MaterialTodo(models.Model):
    _name = 'material.todo'
    _description = 'Material Todo Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, create_date desc'
    
    # 基本欄位
    name = fields.Char(string='待辦事項名稱', required=True, default=lambda self: _('New'))
    sequence = fields.Integer(string='序號', default=10)
    model_name = fields.Char(string='模型名稱', required=True, index=True)
    res_id = fields.Integer(string='表單ID', required=True, index=True)
    record_name = fields.Char(string='表單名稱', compute='_compute_record_name', store=True)
    # 關聯到具體記錄的參考欄位（可點擊的連結）
    record_ref = fields.Reference(
        string='關聯表單',
        selection='_selection_target_model',
        compute='_compute_record_ref',
        store=True,  # 需要存儲以便前端顯示
        readonly=True
    )
    
    # HTML 連結字段（用於顯示可點擊的連結）
    record_link = fields.Html(
        string='關聯表單連結',
        compute='_compute_record_link',
        store=False,  # 不存儲，動態計算
        sanitize=False,  # 允許 HTML
        readonly=True
    )
    # Todo by人員
    user_id = fields.Many2one(
        'res.users',
        string='待辦人員',
        required=True,
        index=True,
        default=lambda self: self.env.user
    )
    # 狀態
    state = fields.Selection([
        ('pending', '待處理'),
        ('in_progress', '進行中'),
        ('done', '已完成'),
        ('cancelled', '已取消')
    ], string='狀態', default='pending', tracking=True)
    # 簽核相關
    review_id = fields.Many2one(
        'tier.review',
        string='簽核記錄',
        ondelete='cascade',
        index=True
    )
    # 時間相關
    date_create = fields.Datetime(string='建立時間', default=fields.Datetime.now)
    date_start = fields.Datetime(string='開始時間')
    date_done = fields.Datetime(string='完成時間')
    # 描述
    description = fields.Text(string='描述')
    # 優先級
    priority = fields.Selection([
        ('0', '低'),
        ('1', '中'),
        ('2', '高'),
        ('3', '緊急')
    ], string='優先級', default='1')
    
    # 計算欄位
    @api.depends('model_name', 'res_id')
    def _compute_record_name(self):
        for todo in self:
            if todo.model_name and todo.res_id:
                try:
                    record = self.env[todo.model_name].browse(todo.res_id)
                    if record.exists():
                        todo.record_name = record.display_name or record.name_get()[0][1]
                    else:
                        todo.record_name = f"{todo.model_name} ({todo.res_id})"
                except Exception:
                    todo.record_name = f"{todo.model_name} ({todo.res_id})"
            else:
                todo.record_name = False
    
    @api.depends('model_name', 'res_id')
    def _compute_record_ref(self):
        for todo in self:
            if todo.model_name and todo.res_id:
                try:
                    # 檢查模型是否存在且在選擇列表中
                    if todo.model_name in self.env:
                        # 檢查模型是否在 _selection_target_model 的選擇列表中
                        selection_models = [model[0] for model in todo._selection_target_model()]
                        if todo.model_name in selection_models:
                            record = self.env[todo.model_name].browse(todo.res_id)
                            if record.exists():
                                todo.record_ref = f"{todo.model_name},{todo.res_id}"
                            else:
                                todo.record_ref = False
                        else:
                            # 如果模型不在選擇列表中，設置為 False
                            todo.record_ref = False
                    else:
                        todo.record_ref = False
                except Exception:
                    todo.record_ref = False
            else:
                todo.record_ref = False
    
    @api.depends('model_name', 'res_id', 'record_name')
    def _compute_record_link(self):
        """計算 HTML 連結"""
        for todo in self:
            if todo.model_name and todo.res_id and todo.record_name:
                try:
                    # 生成可點擊的 HTML 連結
                    url = f"/web#model={todo.model_name}&id={todo.res_id}"
                    todo.record_link = f'<a href="{url}" target="_blank" class="o_form_uri">{todo.record_name}</a>'
                except Exception:
                    todo.record_link = False
            else:
                todo.record_link = False
    
    def _selection_target_model(self):
        """返回可選的模型列表，動態獲取所有有 tier validation 的模型"""
        # 獲取所有有 tier validation 的模型
        # 在 Odoo 中，tier.definition 記錄了哪些模型有 tier validation
        # 使用 sudo() 來繞過 tier.definition 的權限檢查
        tier_definitions = self.env['tier.definition'].sudo().search([])
        
        # 收集所有唯一的模型
        model_names = set()
        for definition in tier_definitions:
            if definition.model_id and definition.model_id.model:
                model_names.add(definition.model_id.model)
        
        # 如果沒有找到 tier definition，使用常見的模型
        if not model_names:
            model_names = {
                'pco',  # 採購變更單
                'part',  # 零件
                'part.bom',  # BOM
                'project.task',  # 任務
                'rfq.flow',  # RFQ流程
                'document.document',  # 文件
                'express.dco',  # 快速DCO
            }
        
        # 只返回實際存在的模型
        valid_models = []
        for model_name in sorted(model_names):
            if model_name in self.env:
                # 使用 sudo() 來繞過 ir.model 的權限檢查
                # 普通用戶沒有 ir.model 的讀取權限，但我們需要模型名稱
                model = self.env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
                if model:
                    valid_models.append((model_name, model.name))
                else:
                    # 如果找不到 ir.model 記錄，使用模型名稱作為顯示名稱
                    valid_models.append((model_name, model_name))
        
        return valid_models
    
    # 動作方法
    def action_start(self):
        """開始處理待辦事項"""
        for todo in self:
            if todo.state == 'pending':
                todo.write({
                    'state': 'in_progress',
                    'date_start': fields.Datetime.now()
                })
    
    def action_done(self):
        """完成待辦事項"""
        for todo in self:
            if todo.state in ('pending', 'in_progress'):
                todo.write({
                    'state': 'done',
                    'date_done': fields.Datetime.now()
                })
    
    def action_cancel(self):
        """取消待辦事項"""
        for todo in self:
            if todo.state != 'cancelled':
                todo.write({
                    'state': 'cancelled'
                })
    
    def action_reopen(self):
        """重新開啟待辦事項"""
        for todo in self:
            if todo.state in ('done', 'cancelled'):
                todo.write({
                    'state': 'pending',
                    'date_start': False,
                    'date_done': False
                })
    
    # 自動建立待辦事項的方法
    @api.model
    def create_from_review(self, review):
        """從 tier.review 建立待辦事項"""
        # 檢查是否已存在相同 review 的待辦事項
        existing = self.search([('review_id', '=', review.id)])
        if existing:
            return existing
        
        # 為每個 reviewer 建立待辦事項
        todos = self.env['material.todo']
        for reviewer in review.reviewer_ids:
            # 根據審核狀態決定待辦事項狀態
            state_mapping = {
                'waiting': 'pending',
                'pending': 'in_progress',
                'approved': 'done',
                'rejected': 'cancelled',
            }
            todo_state = state_mapping.get(review.status, 'pending')
            
            todo_vals = {
                'name': f"{review.name or '審核'} - {reviewer.name}",
                'model_name': review.model,
                'res_id': review.res_id,
                'user_id': reviewer.id,
                'review_id': review.id,
                'description': f"簽核事項: {review.name or '審核'}\n表單: {review.model} ({review.res_id})",
                'priority': '1',  # 默認為中，因為 Odoo 19 的 tier.definition 沒有 priority 字段
                'state': todo_state,
            }
            todo = self.create(todo_vals)
            todos += todo
        
        return todos
    
    # 覆寫 create 方法以自動生成名稱
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('material.todo') or _('New')
        return super().create(vals_list)
    
    # 約束條件
    @api.constrains('model_name', 'res_id')
    def _check_record_exists(self):
        for todo in self:
            if todo.model_name and todo.res_id:
                try:
                    if todo.model_name in self.env:
                        record = self.env[todo.model_name].browse(todo.res_id)
                        if not record.exists():
                            raise ValidationError(_("關聯的表單不存在！"))
                    else:
                        raise ValidationError(_("模型 '%s' 不存在！") % todo.model_name)
                except Exception:
                    raise ValidationError(_("無法驗證關聯表單的有效性！"))