from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("pr")
        return res
    
class TestModel(models.Model):
    _name = "pr"
    _description = "PR management main model for OpenPLM."
    _inherit = ['mail.thread','mail.activity.mixin', "tier.validation"]

    # 添加审批
    # # _state_name = ["New"]
    _state_field = "state"
    _state_from = ["1","2"]
    _state_to = ["2","3"]
    _tier_validation_manual_config = False
    
    item_number =fields.Char("問題單編號" , default=lambda self: _('New'), copy=False , readonly=True )
    title =fields.Char("標題",required=True)
    classification =fields.Selection(
        string="問題來源",
        selection=[('廠內','廠內'),('供應商','供應商')],
        readonly=False,required=True
    )
    priority =fields.Selection(
        string="優先度",
        selection=[('其他','其他'),('停工','停工'),('重要','重要'),('緊急','緊急')],
        readonly=False
    )

    owner_id = fields.Many2one('res.users', string='權責單位擔當/資材')
    manager_id = fields.Many2one('res.users', string='權責單位主管')  
    quantity =fields.Integer(string="數量")
    team_id = fields.Many2one('res.groups', string='團隊')
    reported_by = fields.Many2one('res.users', string='問題回報人' ,required=True)
    description =fields.Text("問題描述",required=True) 
    environment =fields.Text("環境說明") 
    events =fields.Text("重現操作順序") 
    phase_caused =fields.Selection(
        string="問題發生階段",
        selection=[('需求申請','需求申請'),('設計基礎','設計基礎'),('層次結構','層次結構'),
                   ('詳細設計','詳細設計'),('專案獨特工藝','專案獨特工藝'),('工藝標準','工藝標準'),
                   ('構建週期','構建週期'),('測試中','測試中'),('啟用中','啟用中')],
        readonly=False
    )
    stage_id = fields.Many2one('pr.stage', string='狀態階段', group_expand='_read_group_stage_ids',
                               copy=False,default=lambda self: self.env['pr.stage'].search([('name', '=', 'New')], limit=1))
    state =fields.Selection(
        string="状态",
        selection=[('1','1'),('2','2'),('3','3')],
        default="1",readonly=True,tracking=1
    )
    customer_id =fields.Many2one('res.partner',string='受影響客戶',required=True)
    customer_contact =fields.Many2one('res.partner',string='客戶/供應商 聯絡人',required=True)
    response_req =fields.Selection(
        string="回應",
        selection=[('Yes','Yes'),('No','No'),('N/A','N/A')]
    )
    bcs_external_number =fields.Char(string="外部單號")
    category_of_root_cause =fields.Selection(
        string="真因類別",
        selection=[('人','人'),('機','機'),('料','料'),
                   ('法','法'),('環','環'),('其他','其他')
                   ]
    )
    responsibility_for_root_cause =fields.Selection(
        string="真因權責單位",
        selection=[('RD','RD'),('製造','製造'),('品保','品保'),
                   ('業務','業務'),('供應商','供應商')
                   ]
    )
    pr_owner = fields.Many2one('res.users', string='權責人員')
    supplier_id =fields.Many2one('res.partner',string='來料供應商')

    project_id =fields.Many2many('project.project',string='關聯項目')
    document_id =fields.Many2many('document',string='關聯文件')
    cad_id =fields.Many2many('cad',string='關聯工程圖')
    part_id =fields.Many2many('product.template',string='關聯物料')



#頁簽[關聯檔案]
    refe_file =fields.Many2many("ir.attachment",
                                relation='pr_refe_file_rel',  # 自訂關聯表名
                                column1='pr_id',  # 關聯表中指向當前模型記錄的欄位元元元名
                                column2='attachment_id',  # 關聯表中指向ir.attachment記錄的欄位名                                           
                                string="關聯檔案")
#頁簽[問題編碼]
    errorcode_id = fields.Many2many('errorcode',string="問題編碼")

#頁簽[預防矯正措施]
    request_source =fields.Selection(
        string="要求來源",
        selection=[('新增需求','新增需求'),('客訴案件','客訴案件'),('員工觀察','員工觀察'),
                   ('風險評估','風險評估'),('管理評審','管理評審'),('內部品質稽核','內部品質稽核'),
                   ('QA檢驗','QA檢驗'),('趨勢資料','趨勢資料'),('流程績效監控','流程績效監控'),('FMEA失效分析','FMEA失效分析')  ],
        readonly=False
    )
    d3 =fields.Text(string="(D3)實行及驗證暫時防堵措施")
    d4 =fields.Text(string="(D4)問題發生原因")    
    d5 =fields.Text(string="(D5)驗證改善對策")    
    d6 =fields.Text(string="(D6)執行永久對策")    
    d7 =fields.Text(string="(D7)預防再發事件")   
    other =fields.Text(string="其他描述")   
    defectquantity =fields.Integer(string="不良數")
    bussiness_id = fields.Many2one('res.users', string='業務擔當')  
    tracking_ids =fields.One2many('pr.tracking','pr_id',string="追蹤紀錄")
    image_field = fields.Image(string="圖片")

    _rec_name = 'title' 
    # 配合控制的属性
    versionflog=fields.Integer(string="换版",default=1)
    # 配合控制的属性 的方法 ！=1 在层级定义那可以控制签核的显示
    def setversionflog(self):
        self.write({"versionflog":False,"create_uid":self.create_uid})
# Seqence 自動領號寫法
    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the pr model """
        for vals in vals_list:
                if vals.get('item_number', _('New')) == _('New'):
                    vals['item_number'] = self.env['ir.sequence'].next_by_code('pr')
        return super().create(vals_list)

  
#定義審核中狀態按鈕
    def action_set_inreview(self):
        # 檢查是否為創建者
        if self.create_uid != self.env.user:
            raise UserError("只有創建者可以推動狀態到審核中")
        # 獲取 In Review 階段
        inreview_stage = self.env['pr.stage'].search([('name', '=', 'In Review')], limit=1)
        # 根據 stage_id.name 判斷並處理
        if self.stage_id.name == 'New':
            # 設置階段為 In Review
            self.stage_id = inreview_stage
            # 收集所有需要通知的用戶
            notification_users = [self.owner_id,self.manager_id,self.reported_by,self.pr_owner,self.bussiness_id]
            # 去除空值並去重
            notification_users = list(set([user for user in notification_users if user]))
            # 如果有需要通知的用戶，則發送通知
            if notification_users:
                self._send_review_notification_to_users(notification_users)
        elif self.stage_id.name == 'In Review':
            raise UserError('已是"審核中"狀態')
        else:
            raise UserError('不可以推到"審核中"狀態')
    def _send_review_notification_to_users(self, users):
        """
        向多個用戶發送通知
        :param users: 用戶列表
        """
        if not users:
            return    
        # 創建消息
        message = self.env['mail.message'].create({
            'body': f"PR問題單 {self.item_number} 已被標記為審核中。請查看相關內容。",
            'subject': f"PR問題單 {self.item_number} 審核中",
            'model': self._name,
            'res_id': self.id,
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_comment').id,
        })
        # 批量創建通知
        notifications = []
        for user in users:
            notifications.append({
                'mail_message_id': message.id,
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox',
                'notification_status': 'ready',
            })
        # 一次性創建所有通知
        self.env['mail.notification'].create(notifications)

#定義已發行狀態按鈕
    def action_set_released(self):
        # 檢查是否為創建者
        if self.create_uid != self.env.user:
            raise UserError("只有創建者可以推動狀態到已發行")
        # 獲取 Released 階段
        released_stage = self.env['pr.stage'].search([('name', '=', 'Released')], limit=1)
        # 根據 stage_id.name 判斷並處理
        if self.stage_id.name == 'In Review':
            # 設置階段為 Released
            self.stage_id = released_stage
            # 收集所有需要通知的用戶
            notification_users = [self.owner_id, self.manager_id, self.reported_by, self.pr_owner, self.bussiness_id]
            # 去除空值並去重
            notification_users = list(set([user for user in notification_users if user]))
            # 如果有需要通知的用戶，則發送通知
            if notification_users:
                self._send_close_notification_to_users(notification_users)
        elif self.stage_id.name == 'Released':
            raise UserError('已是"已發行"狀態')
        else:
            raise UserError('不可以推到"已發行"狀態')

# 已發行新增發送即時通知的方法
    def _send_close_notification_to_users(self, users):
        """
        向多個用戶批量發送通知
        :param users: 用戶列表
        """
        if not users:
            return
        # 創建消息
        message = self.env['mail.message'].create({
            'body': f"PR問題單 {self.item_number} 已被標記為已發行。請查看相關內容。",
            'subject': f"PR問題單 {self.item_number} 已發行",
            'model': self._name,
            'res_id': self.id,
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_comment').id,
        })

        # 批量創建通知
        notifications = []
        for user in users:
            notifications.append({
                'mail_message_id': message.id,
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox',
                'notification_status': 'ready',
            })
        # 一次性創建所有通知
        self.env['mail.notification'].create(notifications)
          

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        domain = [('id', 'in', stages.ids)]
        stage_ids = stages.sudo()._search(domain, order=stages._order)
        return stages.browse(stage_ids)

    def write(self, vals):
        vals['create_uid'] =self.create_uid
        # is_setflog =False
        # for record in self.pco_product_id: 
        #     if record.new_affected_product_id and  record.new_affected_product_id.stage_id.name == 'confirmed':                
        #        is_setflog= True
            
        # for record in self.pco_bom_ids: 
        #     if record.new_affected_bom_id != False and  record.new_affected_bom_id.stage_id.name == 'In Review'  :                
        #        is_setflog= True
        # if is_setflog :
        #     res =  super(TestModel, self).write(vals)
        #     return res   
        res =  super(TestModel, self).write(vals)
        return res