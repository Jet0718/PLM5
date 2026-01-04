from odoo import models, fields

class PartStage(models.Model):
    _name = 'partbom.stage'
    _fold_name = 'folded'
    _description = 'Part Bom Stage'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='名稱', required=True)
    description = fields.Char(string='描述', required=True)
    sequence = fields.Integer(string='序號', default=1)
    folded = fields.Boolean(string='摺疊')
