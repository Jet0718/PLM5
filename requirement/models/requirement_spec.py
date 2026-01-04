from odoo import api,fields, models
from datetime import timedelta

class requirement_purpose(models.Model):
    _name = "requirement.spec"
    _description = "spec lib model for require management. "
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name =fields.Char("名称",required=True)
    description = fields.Char("说明")
    # spec_lineid =fields.Many2one('requirement.specline',string ='关联')

class requirement_purpose(models.Model):
    _name = "requirement.specline"
    _description = "spec line lib model for require management. "
    _inherit = ['mail.thread','mail.activity.mixin']
    
    reqstr =fields.Char("要求")
    spec_id =fields.Many2one('requirement.spec',string ='规格')
    spec_name = fields.Char("名称",related='spec_id.name')
    requirement_id =fields.Many2one('requirement',string ='需求评估')