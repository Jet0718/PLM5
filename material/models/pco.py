from odoo import api,fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError

class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("pco")
        return res

class PCOModel(models.Model):
    _name = "pco"
    _description = "PCO main model for OpenPLM."
    _inherit = ['mail.thread','mail.activity.mixin', "tier.validation"]

    # 添加审批
    _state_field = "state"
    _state_from = ["New","Review"]
    _state_to = ["Review","Approved"]
    _tier_validation_manual_config = False
        
    item_number =fields.Char("編號" , default=lambda self: _('New'), copy=False , readonly=True )
    title=fields.Char("主旨" ,required=True,readonly=False,default=" ") 
    description=fields.Char("說明")
    flow_class =fields.Selection(
        string="審批類別",
        selection=[('Product','產品'),('Bom','物料清單')]
    )
    #  required=True
    # flow_class_bom =fields.Selection(
    #     string="Bom審批",
    #     selection=[('Product','产品'),('Bom','物料清单')],
    #     required=True
    # )
    owner_id =fields.Many2one('res.users',string='責任人',default=lambda self: self.env.user)
    contactor_id =fields.Many2one('res.users',string='核決者',required=True)  
    tag_ids = fields.Many2many('pco.tag', string='Tags')
    state =fields.Selection(
        string="状态",
        selection=[('New','草稿'),('Review','審核中'),('Approved','核准'),('Cancel','取消')],
        default="New",readonly=True,tracking=1
    )
    active =fields.Boolean("啟用",default=True) 
    pco_product_id =fields.One2many('pco.product','pco_id_prd',string=' ')

    classstr = fields.Many2many('pco.type', string='審批類別',required=True)


    # #上传单个档案写法
    # binary_field = fields.Binary("档案")
    # binary_file_name =fields.Char("档案名称")
    # #上传多个档案写法
    refe_file =fields.Many2many("ir.attachment",
                                relation='pco_refe_file_rel',  # 自訂關聯表名
                                column1='pdo_id',  # 關聯表中指向當前模型記錄的欄位元元元名
                                column2='attachment_id',  # 關聯表中指向ir.attachment記錄的欄位名                                           
                                string="關聯檔案")
    versionflog=fields.Integer(string="換版",default=1)


    showproduct=fields.Integer(string="顯示part",default=1)
    showbom=fields.Integer(string="顯示bom",default=1)
    pco_bom_ids =fields.One2many('pco.bom','pco_id_bom',string=' ')
    
    # 增加關聯問題單 及 數量
    # pr_ids = fields.One2many('pr','pco_id')
    pr_count =fields.Integer("數量" ,compute='_compute_pr_count')
    
    # Seqence 自動領號寫法
    @api.model_create_multi
    def create(self, vals_list):
         """ Create a sequence for the requirement model """
         for vals in vals_list:
               if vals.get('item_number', _('New')) == _('New'):
                      vals['item_number'] = self.env['ir.sequence'].next_by_code('pco')
               return super().create(vals_list)     
    
    #定義按鈕
    def action_set_Review(self):
        if self.state =='Review':
            # self.write ({'state':'Review'})             
            names=""
            for record in self.pco_product_id: 
                # names=names+"," +record.affected_product_id.name
                
             # 退回后需要判斷是否已經換版
                if len(record.new_affected_product_id) !=0 :
                    
                    befor_version=record.affected_product_id.version
                    after_version=record.new_affected_product_id.version
                    if after_version ==befor_version+1:
                        continue
            #ebert version item 換版 條件判斷送審物件的版本是否是1， 是則送審發布，否則換版
                if record.affected_product_id.version !=0  or record.affected_product_id.stage_id.name == 'Released':
                    
                    
                    # 用對應的product進行 plm的方法變更送審
                    # product = self.env['product.product'].search([('item_number', "=", record.affected_product_id.item_number),
                    #                                               ('version','=',record.affected_product_id.version),
                    #                                               ('default_code','=',record.affected_product_id.item_number +'_01_'+
                    #                                                str(record.affected_product_id.version))])
                    # if not product :
                    #     product = self.env['product.product'].search([('product_tmpl_id', "=", record.affected_product_id.id),
                    #                                                 ('version','=',record.affected_product_id.version)],
                    #                                                 limit=1)
                    
                    # product_id = product.id
                    # active_model = 'product.product'
                    # old_product_product_id = self.env[active_model].browse(product_id)
                    # old_product_template_id = old_product_product_id.product_tmpl_id
                    # # old_product_template_id.new_version()
                    # code = str(record.affected_product_id.version+1)
                    # record.new_affected_product_id = record.affected_product_id.sudo().copy(default={
                    #     'version': record.affected_product_id.version + 1,
                    #     'active': False,
                    #     'cnis_current': False,
                    #     'code': record.affected_product_id.item_number+"-"+code,
                    # })
                    # new_product_template_id = old_product_product_id.product_tmpl_id.get_next_version()         
                        
                    # # new_product_id = self.env['product.product'].search([('product_tmpl_id','=', new_product_template_id.id)], limit=1)
                    # # new_product_id = self.env['product.product'].search([('product_tmpl_id','=', old_product_product_id.product_tmpl_id.id)], limit=1)

                    # # raise UserError(product.item_number)
                    # ecode = record.affected_product_id.item_number
                    # eversion = record.affected_product_id.version+1

                    # # newrecord = self.env['product.template'].search([('item_number', '=' ,ecode ),('version', '=' ,eversion)])
                    
                    # newrecord = self.env['product.template'].search([('cn_configid', '=' ,old_product_template_id.cn_configid ),('version','=',eversion)])

                    # newrecord.write({'cn_configid': record.affected_product_id.cn_configid,'cnis_current': True})
                    # record.affected_product_id.write({'cnis_current': False,'stage_id':4,'stage_id':4})
                    
                    # record.write({'new_affected_product_id': newrecord.id})
                    # self.write({'btnflog': False})

                    if not record.new_affected_product_id:
                            code = str(record.affected_product_id.version+1)
                            record.new_affected_product_id = record.affected_product_id.sudo().copy(default={
                                'version': record.affected_product_id.version + 1,
                                'active': False,
                                'item_number': record.affected_product_id.item_number,
                                'name': record.affected_product_id.name,
                            })
                            #抄寫內部參考號 編號-版本
                            record.affected_product_id.write ({'active':True,'stage_id':4})
                            # 根據 affected_product_id 的狀態變更落實到 affected_bom_id 上
                            # 找到與產品相關的所有 BOM 並更新狀態為 On Change (4)
                            boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.affected_product_id.id)])
                            for bom in boms:
                                # 只有當 BOM 狀態不是 Superseded 時才更新
                                if bom.stage_id.name != 'Superseded':
                                    bom.write({'stage_id': 4})  # On Change
                                    bom.write({'cnis_current': True})
                            record.write({'new_affected_product_id':record.new_affected_product_id.id})
                        
                else :
                    
                    # default_code = str(record.affected_product_id.version)
                    product = self.env['product.product'].search([('item_number', "=", record.affected_product_id.item_number),('version','=',record.affected_product_id.version),('default_code','=',record.affected_product_id.item_number +'_01_'+str(record.affected_product_id.version))])
                    if not product :
                        product = self.env['product.product'].search([('product_tmpl_id', "=", record.affected_product_id.id),
                                                                    ('version','=',record.affected_product_id.version)],
                                                                    limit=1)
                    
                    # product.action_confirm()
                    # product.write({'stage_id':})
                    record.affected_product_id.write({'stage_id':2})
                    # 根據 affected_product_id 的狀態變更落實到 affected_bom_id 上
                    # 找到與產品相關的所有 BOM 並更新狀態為 In Review (2)
                    boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.affected_product_id.id)])
                    for bom in boms:
                        # 只有當 BOM 狀態是 New 或 In Review 時才更新為 In Review
                        if bom.stage_id.name in ['New', 'In Review']:
                            bom.write({'stage_id': 2})  # In Review
                    # record.affected_product_id.write({'default_code':default_code})
                    record.write({'new_affected_product_id':record.affected_product_id.id})

            for record in self.pco_bom_ids: 
                if record.affected_bom_id != False :
                    #if self.producaffected_product_idtion_id:
                    # This ECO was generated from a MO. Uses it MO as base for the revision.

                    # 退回後需要判斷是否已經換版
                    if len(record.new_affected_bom_id) !=0 :
                        befor_version=record.affected_bom_id.version
                        after_version=record.new_affected_bom_id.version
                        if after_version ==befor_version+1:
                            continue
                    if record.affected_bom_id.version !=0  or record.affected_bom_id.stage_id.name == 'Released':
                        
                        if not record.new_affected_bom_id:
                            code = str(record.affected_bom_id.version+1)
                            record.new_affected_bom_id = record.affected_bom_id.sudo().copy(default={
                                'version': record.affected_bom_id.version + 1,
                                'active': False,
                                # 'cnis_current': False,
                                # 'code': record.affected_bom_id.item_number+"-"+code,
                            })
                            #抄寫內部參考號 編號-版本
                            record.affected_bom_id.write ({'active':True}) 
                            record.affected_bom_id.write({'stage_id':4}) 
                            record.affected_bom_id.write({'cnis_current':True})
                            record.write({'new_affected_bom_id':record.new_affected_bom_id.id})   
                            # self.write({'btnflog': False})
                    else :
                        code = str(record.affected_bom_id.version+1)
                        # 修正：BOM 應該先變為 In Review (2)，而不是直接變為 Released (3)
                        record.affected_bom_id.write({'stage_id':2})  # In Review
                        record.affected_bom_id.write({'code':code})
                        record.write({'new_affected_bom_id':record.affected_bom_id.id})
                   
                    
            # ebert end             
             
        # elif self.state =='Review':
        #     raise UserError('已是"審核中"狀態')
        else:
            raise UserError('不可以推到"審核中"狀態')
   
    def action_set_Review_after(self):
        for record in self.pco_product_id:
            if record.new_affected_product_id:
                record.new_affected_product_id.write({'stage_id':2})
                # 根據 affected_product_id 的狀態變更落實到 affected_bom_id 上
                # 找到與新版本產品相關的所有 BOM 並更新狀態為 In Review (2)
                boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.new_affected_product_id.id)])
                for bom in boms:
                    # 只有當 BOM 狀態是 New 或 In Review 時才更新為 In Review
                    if bom.stage_id.name in ['New', 'In Review']:
                        bom.write({'stage_id': 2})  # In Review
                # product = self.env['product.product'].search([('item_number', "=", record.new_affected_product_id.item_number),('version','=',record.new_affected_product_id.version),('default_code','=',record.new_affected_product_id.item_number +'_01_'+str(record.new_affected_product_id.version))])
                # if not product :
                #         product = self.env['product.product'].search([('product_tmpl_id', "=", record.new_affected_product_id.id),
                #                                                     ('version','=',record.new_affected_product_id.version)],
                #                                                     limit=1)
                # if product.stage_id.name == 'New':
                #     product.action_confirm()

        for record in self.pco_bom_ids:
            if record.new_affected_bom_id != False  :
                record.new_affected_bom_id.write({'stage_id':2})
        # for record in self :
            
            # record.write({'btnflog': True})
        # elif self.state =='Review':
        #     raise UserError('已是"變更後審核"狀態')
        # else:
        #     raise UserError('不可以推到"變更後審核"狀態')  

    def action_set_Approved(self):
        if self.state =='Approved':
            # self.write({'state':'Approved'})
    #          #ebert 发布 Released
            for record in self.pco_product_id:
                if record.affected_product_id :
                    if  record.affected_product_id.stage_id.name == 'On Change' :
                        record.affected_product_id.write({'stage_id':5,'active':False})
                        record.new_affected_product_id.write({'active':True,'stage_id':3})
                        # 根據 affected_product_id 的狀態變更落實到 affected_bom_id 上
                        # 找到與舊版本產品相關的所有 BOM 並更新狀態為 Superseded (5)
                        boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.affected_product_id.id)])
                        for bom in boms:
                            # 更新舊版本 BOM 為 Superseded
                            bom.write({'stage_id': 5})  # Superseded
                            bom.write({'active': False})
                        # 同時更新新版本產品相關的 BOM 為 Released (3)
                        new_boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.new_affected_product_id.id)])
                        for bom in new_boms:
                            # 只有當 BOM 狀態是 In Review 或 On Change 時才更新為 Released
                            if bom.stage_id.name in ['In Review', 'On Change']:
                                bom.write({'active': True})
                                bom.write({'stage_id': 3})  # Released

                    else :
                        record.affected_product_id.write({'stage_id':3})
                        # 根據 affected_product_id 的狀態變更落實到 affected_bom_id 上
                        # 找到與產品相關的所有 BOM 並更新狀態為 Released (3)
                        boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.affected_product_id.id)])
                        for bom in boms:
                            # 只有當 BOM 狀態是 In Review 時才更新為 Released
                            # 避免從 New 直接跳到 Released
                            if bom.stage_id.name == 'In Review':
                                bom.write({'stage_id': 3})  # Released
            for record in self.pco_bom_ids:
                    if record.affected_bom_id :
                        #if self.producaffected_product_idtion_id:
                        # This ECO was generated from a MO. Uses it MO as base for the revision.

                        if record.affected_bom_id.version !=0  or record.affected_bom_id.stage_id.name == 'On Change':
                            record.affected_bom_id.write({'stage_id':5})
                            record.affected_bom_id.write({'active':False})
                            record.new_affected_bom_id.write({'active':True})
                            # 只有當新 BOM 狀態是 In Review 或 On Change 時才更新為 Released
                            if record.new_affected_bom_id.stage_id.name in ['In Review', 'On Change']:
                                record.new_affected_bom_id.write({'stage_id':3})
                        else :
                            # 只有當新 BOM 狀態是 In Review 時才更新為 Released
                            if record.new_affected_bom_id.stage_id.name == 'In Review':
                                record.new_affected_bom_id.write({'stage_id':3})

                        
    #         # ebert end 
             
        # elif self.state =='Approved':
        #     raise UserError('已是"核准"狀態')
        elif self.state =='Cancel':
            raise UserError('已取消,不能被核准')
        else:
            raise UserError('不可以推到"核准"狀態')
        
    def action_set_Cancel(self):
        for nd in self.pco_product_id:                
            if nd.new_affected_product_id and nd.new_affected_product_id.version !=1 :
                raise UserError('已換版,不能被取消')
        for nd in self.pco_bom_ids:                
            if nd.new_affected_bom_id.version !=1 :
                raise UserError('已換版,不能被取消')
        if self.state =='New':
            self.write({'state':'Cancel'})
        elif self.state =='Review':
            self.write({'state':'Cancel'})             
        elif self.state =='Cancel':
            raise UserError('已是"取消"狀態')
        else:
            raise UserError('已核准,不能被取消')
        

    def product_create_new_revision_by_server(self):
        product_id = self.id
        active_model = 'product.product'
        if product_id and active_model:
            old_product_product_id = self.env[active_model].browse(product_id)
            old_product_template_id = old_product_product_id.product_tmpl_id
            old_product_template_id.new_version()
            new_product_template_id = old_product_product_id.product_tmpl_id.get_next_version()         
            
            new_product_id = self.env['product.product'].search([('product_tmpl_id','=', new_product_template_id.id)], limit=1)
            return new_product_id  
            
   
    # @api.onchange('pco_product_id')
    # def _compute_pco_product_id(self):
    def write(self, vals):
        vals['create_uid'] =self.create_uid
        is_setflog =False
        for record in self.pco_product_id: 
            if record.new_affected_product_id and  record.new_affected_product_id.stage_id.name == 'confirmed':                
               is_setflog= True
            
        for record in self.pco_bom_ids: 
            if record.new_affected_bom_id != False and  record.new_affected_bom_id.stage_id.name == 'In Review'  :                
               is_setflog= True
        if is_setflog :
            res =  super(PCOModel, self).write(vals)
            return res   
        res =  super(PCOModel, self).write(vals)
        return res

    def setversionflog(self):
        for record in self:
            for nd in record.pco_product_id:                
                if nd.affected_product_id.stage_id.name =="Released" :
                    versionflog= False  
                    self.write({"versionflog":versionflog,"create_uid":self.create_uid})
            for nd in record.pco_bom_ids:                
                if nd.affected_bom_id.stage_id.name =="Released" :
                    versionflog= False  
                    self.write({"versionflog":versionflog,"create_uid":self.create_uid})
    
    def do_reject(self):
        # 將 PCO 狀態設為 New
        self.write({"state":'New',"create_uid":self.create_uid})
        # 更新所有相關產品的狀態從 In Review 回到 New
        for record in self:
            for nd in record.pco_product_id:
                if nd.affected_product_id:
                    # 如果產品狀態是 In Review (2)，則設為 New (1)
                    if nd.affected_product_id.stage_id.name == 'In Review':
                        nd.affected_product_id.write({'stage_id': 1})  # New
                    # 如果新版本產品存在且狀態是 In Review，也設為 New
                    if nd.new_affected_product_id and nd.new_affected_product_id.stage_id.name == 'In Review':
                        nd.new_affected_product_id.write({'stage_id': 1})  # New
            # 更新所有相關 BOM 的狀態從 In Review 回到 New
            for nd in record.pco_bom_ids:
                if nd.affected_bom_id:
                    # 如果 BOM 狀態是 In Review (2)，則設為 New (1)
                    if nd.affected_bom_id.stage_id.name == 'In Review':
                        nd.affected_bom_id.write({'stage_id': 1})  # New
                    # 如果新版本 BOM 存在且狀態是 In Review，也設為 New
                    if nd.new_affected_bom_id and nd.new_affected_bom_id.stage_id.name == 'In Review':
                        nd.new_affected_bom_id.write({'stage_id': 1})  # New


    #退回检查
    def reject_chk(self):
        for record in self:
            for nd in record.pco_product_id:                
                if nd.new_affected_product_id and nd.new_affected_product_id.version !=1 :
                    raise UserError('已核准,不能被取消')
            for nd in record.pco_bom_ids:                
                if nd.new_affected_bom_id.version !=1 :
                    raise UserError('已換版,不能被取消')
    @api.onchange('classstr')
    def _compute_classstr(self):
        self.write({'showproduct':1})
        self.write({'showbom':1})
        for r in self.classstr:
            if r.name=="Product":
                self.write({'showproduct':0})
            if r.name=="Bom":
                self.write({'showbom':0})

    #計算關聯問題單的數量
    @api.depends()
    def _compute_pr_count(self):
        for record in self:
            try:
                record.pr_count = self.env['pr'].search_count([('pco_id', '=', record.id)])
            except Exception as e:
                record.pr_count = 0

    def pr_model_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': '問題單',
            'view_mode': 'list,form',
            'res_model': 'pr',
            'domain': [('pco_id', '=', self.id) ],
            'context': {'default_pco_id': self.id},
        }

    def action_create_pr(self):
        """建立一筆新的 PR 記錄，並複製 title 和 description"""
        self.ensure_one()
        # 建立新的 PR 記錄
        pr_vals = {
            'title': self.title,
            'description': self.description,
            'pco_id': self.id,
        }
        pr_record = self.env['pr'].create(pr_vals)
        # 開啟新建立的 PR 表單視圖
        return {
            'type': 'ir.actions.act_window',
            'name': '問題單',
            'view_mode': 'form',
            'res_model': 'pr',
            'res_id': pr_record.id,
            'target': 'current',
        }

