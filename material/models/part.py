from odoo import api,fields, models,_, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import UserError 

class Part(models.Model):
    _inherit = "product.template"
    _description = "Material management main model of part."

    material_number =fields.Char(string="正式料號")
    # item_number =fields.Char("PLM編號" , default=lambda self: _('New'), copy=False )
    item_number =fields.Char("PLM編號" , default=lambda self: _('New'), copy=False , readonly=True )
    classification =fields.Selection(
        string="類別",
        selection=[('商品存貨','商品存貨'),('成品','成品'),('雷射模組','雷射模組'),
                   ('PCBA','PCBA'),('原物料_LD_LED','原物料_LD_LED'),('原料','原料'),
                   ('模具品','模具品'),('A_需列管','A_需列管'),('B_不需列管','B_不需列管')],
        readonly=False,required=True
    )
   
    spec =fields.Char(string="規格")
    description =fields.Char(string="料件說明")
    make_buy =fields.Selection(
        string="料件屬性",
        selection=[('P:採購件','P:採購件'),('M:自製件','M:自製件'),('S:託外加工件','S:託外加工件'),
                   ('Y:虛設品號','Y:虛設品號'),('F:Feature件','F:Feature件'),('O:Option件','O:Option件')],
        readonly=False,required=True
    )
    units =fields.Selection(
        string="單位",
        selection=[('EA','EA'),('IN','IN'),('FT','FT'),
                   ('MM','MM'),('CM','CM'),('M','M')],
        readonly=False,required=True
    )
    # version =fields.Char(string="版本")
    version=fields.Integer(string="版本",default=0,copy=False,readonly=True)
    # version=fields.Integer(string="版本",default=0,copy=False)
    # image_field = fields.Image(string="图片")
    owner_id = fields.Many2one('res.users', string='料號擁有者')
    department_id = fields.Many2one('res.users', string='物料管理部門')
    team_id = fields.Many2one('res.groups', string='團隊')
    stage_id = fields.Many2one('part.stage', string='狀態階段', group_expand='_read_group_stage_ids',
                               copy=False,default=lambda self: self.env['part.stage'].search([('name', '=', 'New')], limit=1))
    effective_date =fields.Date("生效日期" ,copy=False )
    released_date =fields.Date("發行日期" ,copy=False )
    accounting =fields.Selection(
        string="會計分類",
        selection=[('1301:商品存貨','1301:商品存貨'),('1311:成品','1311:成品'),('1313:半成品','1313:半成品'),
                   ('1315:原料','1315:原料'),('1316:物料','1316:物料'),('9999:費用/收入類/其他','9999:費用/收入類/其他')],
        readonly=False
    )
    replenishment =fields.Selection(
        string="補貨政策",
        selection=[('R:依補貨點','R:依補貨點'),('M:依MRP需求','M:依MRP需求'),('L:依LRP需求','L:依LRP需求'),
                   ('N:不需','N:不需'),('H:依歷史銷售','H:依歷史銷售')],
        readonly=False
    )
    inspection =fields.Selection(
        string="檢驗方式",
        selection=[('0:免檢','0:免檢'),('1:抽檢(減量)','1:抽檢(減量)'),('2:抽檢(正常)','2:抽檢(正常)'),
                   ('3:抽檢(加嚴)','3:抽檢(加嚴)'),('4:全檢 ','4:全檢 ')],
        readonly=False
    )

    batchnumber =fields.Selection(
        string="批號管理",
        selection=[('N:不需要','N:不需要'),('Y:需要不檢查庫存量','Y:需要不檢查庫存量'),('W:僅需警告','W:僅需警告'),
                   ('T:需要且檢查庫存量','T:需要且檢查庫存量')],
        readonly=False
    )
    part_file =fields.Many2many("ir.attachment",
                                relation='part_file_rel',  # 自訂關聯表名
                                column1='part_id',  # 關聯表中指向當前模型記錄的欄位元元元名
                                column2='attachment_id',  # 關聯表中指向ir.attachment記錄的欄位名                                           
                                string="關聯檔案")

    part_class_ids =fields.One2many('part.class','part_id',string="物料分類內容")

    document_id =fields.Many2many('document',string='關聯文件')
    cad_id =fields.Many2many('cad',string='關聯工程圖')
    
    # display_name =fields.Char(string="Keyname" , compute ='_compute_display_name',store=True)

    # _rec_name = 'display_name' 
    _rec_name = 'name' 

    # @api.depends('item_number')
    # def _compute_display_name(self):
    #     for record in self:
    #         record.display_name = f"{record.item_number}"


 # Seqence 自動領號寫法
    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the part model """
        for vals in vals_list:
                if vals.get('item_number', _('New')) == _('New'):
                    vals['item_number'] = self.env['ir.sequence'].next_by_code('part')
        return super().create(vals_list)



    @api.onchange('classification')
    def _onchange_classification(self):
        if self.classification:
            # 清空现有的 part_class_ids
            self.part_class_ids = [(5, 0, 0)]
            # 从 class_template 中获取与 classification 相同的内容
            class_templates = self.env['class.template'].search([('classification', '=', self.classification)])
            # 创建新的 part_class_ids 记录
            for template in class_templates:
                self.part_class_ids = [(0, 0, {
                    'classification': template.classification,  # 确保设置 classification
                    'name': template.name,  # 确保设置 name
            })]
   
#定義審核中狀態按鈕
    def action_set_inreview(self):
        # 檢查是否為創建者
        if self.create_uid != self.env.user:
            raise UserError("只有創建者可以推動狀態到審核中")
        # 獲取 In Review 階段
        inreview_stage = self.env['part.stage'].search([('name', '=', 'In Review')], limit=1)
        # 根據 stage_id.name 判斷並處理
        if self.stage_id.name == 'New':
            # 設置階段為 In Review
            self.stage_id = inreview_stage
            # 收集所有需要通知的用戶
            notification_users = [self.owner_id,self.department_id]
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
            'body': f"物料表 {self.item_number} 已被標記為審核中。請查看相關內容。",
            'subject': f"物料表 {self.item_number} 審核中",
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
        released_stage = self.env['part.stage'].search([('name', '=', 'Released')], limit=1)
        # 根據 stage_id.name 判斷並處理
        if self.stage_id.name == 'In Review':
            # 設置階段為 Released
            self.stage_id = released_stage
            # 收集所有需要通知的用戶
            notification_users = [self.owner_id,self.department_id]
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
            'body': f"物料表 {self.item_number} 已被標記為已發行。請查看相關內容。",
            'subject': f"物料表 {self.item_number} 已發行",
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

