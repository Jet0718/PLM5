from odoo import fields, models;


class DocumentState(models.Model):
    _name = 'document.state'
    _description = 'Document State'
    _order = 'sequence'

    # 狀態名稱
    name = fields.Char(string='狀態名稱', required=True)
    # 狀態描述
    description = fields.Text(string='狀態描述')
    # 狀態序號
    sequence = fields.Integer(string='狀態序號', default=1)
    # 折疊
    folded = fields.Boolean(string='折疊', default=False)