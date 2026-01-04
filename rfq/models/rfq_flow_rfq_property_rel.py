from odoo import models, fields, api;

class RfqFlowRfqPropertyRel(models.Model):
    _name = 'rfq.flow.rfq.property.rel'
    _description = '送審RFQ與RFQ流程關系表'
    _table = 'rfq_flow_rfq_property_rel'  # 顯式指定表名


    rfq_flow_id = fields.Many2one('rfq.flow', string='RFQ Flow', required=True)
    rfq_property_id = fields.Many2one('rfq.property', string='RFQ Property', required=True)
    link_time = fields.Datetime(string='關聯時間', default=fields.Datetime.now)
    link_user_id = fields.Many2one('res.users', string='關聯用戶', default=lambda self: self.env.user)
