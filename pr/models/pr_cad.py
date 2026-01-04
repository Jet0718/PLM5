from odoo import fields, models,api,_

class PrCad(models.Model):
    _inherit = "cad"
    # 增加關聯問題單 及 數量
    pr_ids = fields.One2many('pr','cad_id')
    pr_count =fields.Integer("數量" ,compute='_compute_pr_count')

#計算關聯問題單的數量
    @api.depends("pr_ids")
    def _compute_pr_count(self):
        for record in self:
            try: 
                record.pr_count = len(record.pr_ids)                
            except Exception as e:                
                record.pr_count =self.env['pr'].search_count([('cad_id', '=', record.id)])

    def pr_model_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': '問題單',
            'view_mode': 'list,form',
            'res_model': 'pr',
            'domain': [('cad_id', '=', self.id) ],
            'context': {'default_cad_id': self.id},
        }