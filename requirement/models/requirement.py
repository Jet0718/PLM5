from odoo import api,fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError

class TestModel(models.Model):
    _name = "requirement"
    _description = "Require management main model for OpenPLM."
    _inherit = ['mail.thread','mail.activity.mixin']
    
    item_number =fields.Char("編號" , default=lambda self: _('New'), copy=False , readonly=True )
    name =fields.Char("需求名称",required=True)
    partner_id =fields.Many2one('res.partner',string='客戶',required=True)    
    contract_name =fields.Char("聯絡人")
    owner_id =fields.Many2one('res.users',string='負責人',default=lambda self: self.env.user)
    prd_type_id =fields.Many2one('product.category',string='需求產品類型')    
    prd_purpose_id =fields.Many2one('requirement.purpose',string='產品用途')  
    sample =fields.Boolean("是否打樣",default=False)
    quotation =fields.Boolean("是否報價",default=False)


    state =fields.Selection(
        string="状态",
        selection=[('Draft','草稿'),('Evaluting','评价'),('Approved','核准'),('Abort','中止')],
        default="Draft",readonly=True,tracking=1
    )
    speical_req =fields.Text("特殊要求")
    ref_product =fields.Many2one('product.template',string='參考產品') 
    active =fields.Boolean("啟用",default=True)    
    spec_ids =fields.One2many('requirement.specline','requirement_id')

    # 2024.9.29 Herbert新增内容:增加关联项目 及 项目数量
    project_ids = fields.One2many('project.project','requirement_id')
    project_count =fields.Integer("数量" ,compute='_compute_project_count')
    lead_ids = fields.One2many('crm.lead','requirement_id')
    lead_count =fields.Integer("数量" ,compute='_compute_lead_count')

    # #上传单个档案写法
    # binary_field = fields.Binary("档案")
    # binary_file_name =fields.Char("档案名称")
    # #上传多个档案写法
    binary_fields =fields.Many2many("ir.attachment",string="Multi Files Upload",domain="[]")

    # Seqence 自动领号写法
    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the requirement model """
        for vals in vals_list:
            if vals.get('item_number', _('New')) == _('New'):
                    vals['item_number'] = self.env['ir.sequence'].next_by_code('requirement')
        res = super().create(vals_list)
        # 同步至ES
        try:
            self.env["elastic.datapost"].post2elastic(res, vals_list[0])
        except Exception:
            pass  # 忽略ES错误
        return res

    # 同步至ES
    def write(self, vals):
        res = super(TestModel, self).write(vals)
        try:
            self.env["elastic.datapost"].post2elastic(self, list(self._fields.keys()))
        except Exception:
            pass  # 忽略ES错误
        return res
     
    def unlink(self):
        try:
            self.env["elastic.datapost"].elasticdelete(self._name + "_" + str(self.id))
        except Exception:
            pass
        return super(TestModel, self).unlink()
      
    
    #定义按钮
    def action_set_Evaluting(self):
        if self.state =='Draft':
            self.write ({'state':'Evaluting'})        
        elif self.state =='Evaluting':
            raise UserError('已是"评价"状态')
        else:
            raise UserError('不可以推到"评价"状态')
    def action_set_Approved(self):
        if self.state =='Evaluting':
            self.write({'state':'Approved'})
        elif self.state =='Approved':
            raise UserError('已是"核准"状态')
        elif self.state =='Abort':
            raise UserError('已中止,不能被核准')
        else:
            raise UserError('不可以推到"核准"状态')
    def action_set_Abort(self):
        if self.state =='Evaluting':
            self.write({'state':'Abort'})
        elif self.state =='Draft':
            self.write({'state':'Abort'})             
        elif self.state =='Abort':
            raise UserError('已是"中止"状态')
        else:
            raise UserError('已核准,不能被中止')
    
    #计算关联Project的数量
    @api.depends("project_ids")
    def _compute_project_count(self):
        for record in self:
            # record.project_count = len(record.project_ids)
            record.project_count = self.env['project.project'].search_count([('requirement_id', '=', record.id)])
    #计算关联Lead的数量
    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for record in self:
            # record.lead_count = len(record.lead_ids)     
            record.lead_count = self.env['crm.lead'].search_count([('requirement_id', '=', record.id)])

    def require_project_filter_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'project',
            'view_mode': 'list,form',
            'res_model': 'project.project',
            'domain': [('requirement_id', '=', self.id) ],
            'context': {'default_requirement_id': self.id},
        }
    def require_leads_filter_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'lead',
            'view_mode': 'list,form',
            'res_model': 'crm.lead',
            'domain': [('requirement_id', '=', self.id) ],
            'context': {'default_requirement_id': self.id},
        }