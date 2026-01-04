from odoo import fields, models,api,_

class Project(models.Model):
    _inherit = "crm.lead"
    # 2024.9.29 Herbert新增内容:增加关联需求
    requirement_id =fields.Many2one('requirement',string='关联需求')