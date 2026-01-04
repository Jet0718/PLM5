from odoo import models, fields, api;
class DocumentEditor(models.Model):
    _name = 'document.editor'
    _description = 'Document Editor'
    _rec_name = 'name'
    _order = 'sequence'

    # 工具名稱
    name = fields.Char(string='工具名稱', required=True)
    # 工具版本
    version = fields.Integer(string='工具版本', required=True,default=0)
    # 序號
    sequence = fields.Integer(string='序號', default=1)
