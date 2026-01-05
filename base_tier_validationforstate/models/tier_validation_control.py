# Copyright 2017 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.misc import frozendict
import logging

_logger = logging.getLogger(__name__)

class TierDefinition(models.Model):
    _name = "tier.definition"
    _inherit = "tier.definition"
    _description = "Tier Definition"

    to_state = fields.Char(string="to state")
    domethod = fields.Char(string="used method")

    # reject_state_parent = fields.Char(string="parent reject state")
    # reject_state_child = fields.Char(string="child reject state")
    reject_method = fields.Char(string="reject method")

    # 202503优化签核之启用默认模式签核
    # 启用默认栏位
    # cnuser_defualt =fields.Boolean("啟用默认",default=False)
    # defp_fldname  =fields.Char("表头栏位名称")
    # defp_shipfdids =fields.Char("父阶关联的属性名称")
    # defcd_orcitmid =fields.Char("送审对象旧版栏位名称")
    # defcd_fldname =fields.Char("送审对象状态栏位名称")
    # defcd_2relstate =fields.Char("送审对象状态变化值")
    
    # defcd_version_fldname =fields.Char("送审对象版本栏位名称")
    # # 匹配值
    # defcd_fldnameisversion =fields.Char("送审对象状态判定变版值")    
    # # 读取需要匹配的栏位，这里是栏位名称
    # defcd_newitemid =fields.Char("送审对象新版栏位名称")
    # defcd_oldstateupda = fields.Char("送审对象旧版状态变化值")
    cnuser_defualt =fields.Boolean("Enable default",default=False)
    defp_fldname  =fields.Char("Header field name")
    defp_shipfdids =fields.Char("parent ship field name")
    defcd_orcitmid =fields.Char("Submission Old field name")
    defcd_fldname =fields.Char("Submission Status field name")
    defcd_2relstate =fields.Char("Submission State change value")
    
    defcd_version_fldname =fields.Char("Submission Version field name")
    # 匹配值
    defcd_fldnameisversion =fields.Char("Submission judge change version value")    
    # 读取需要匹配的栏位，这里是栏位名称
    defcd_newitemid =fields.Char("Submission Status field name")
    defcd_oldstateupda = fields.Char("Submission Old version status change value")

    review_type = fields.Selection(
        selection_add=[("multiple_individuals", "Multiple specific users")],
        ondelete={"multiple_individuals": "set default"},
    )
    reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        string="Reviewers",
        domain="[('id', '!=', 1)]",
    )
    notify_reminder_delay = fields.Integer(
        string="Send reminder message on pending reviews",
        help="Number of days after which a message must be posted to remind about "
        "pending validation  (0 = no reminder)",
        default=3,
    )
    is_selected = fields.Boolean(string="选中", default=False)

    def select_row(self):
        context = self.env.context

    def action_on_close(self):
        context = self.env.context

        # 获取选中的记录 ID
        selected_ids = context.get('active_ids', [])

    @api.onchange('review_type')
    def onchange_review_type(self):
        super().onchange_review_type()
        if self.review_type == 'multiple_individuals':
            self.approve_sequence = False

    def write(self, vals):
        # Ensure approve_sequence is False for multiple_individuals
        if 'review_type' in vals and vals['review_type'] == 'multiple_individuals':
            vals['approve_sequence'] = False
        elif 'approve_sequence' in vals and vals['approve_sequence']:
            # If trying to set approve_sequence True for multiple_individuals, prevent it
            for rec in self:
                if rec.review_type == 'multiple_individuals':
                    vals['approve_sequence'] = False
        return super().write(vals)

    @api.constrains('review_type', 'approve_sequence')
    def _check_approve_sequence_for_multiple_individuals(self):
        for record in self:
            if record.review_type == 'multiple_individuals' and record.approve_sequence:
                raise ValidationError(
                    _('Approve by sequence cannot be enabled for Multiple specific users review type.')
                )

    # reject_nodes = fields.Many2one('tier.definition', string='Reject to')

class TierReview(models.Model):
    _name = "tier.review"
    _inherit = "tier.review"


    status = fields.Selection(
        [
            ("waiting", "Waiting"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("approved", "Approved"),
            ("goback", "Rejected"),
        ],
        default="waiting",
    )
    specific_reviewer_id = fields.Many2one(
        comodel_name="res.users",
        string="Specific Reviewer",
        help="Specific reviewer assigned for multiple_individuals review type.",
    )
    to_state = fields.Char(related="definition_id.to_state", readonly=True)
    domethod = fields.Char(related="definition_id.domethod", readonly=True)

    # reject_state_parent = fields.Char(related="definition_id.reject_state_parent", readonly=True)
    # reject_state_child = fields.Char(related="definition_id.reject_state_child", readonly=True)

    reject_method = fields.Char(related="definition_id.reject_method", readonly=True)

    # 202503优化签核之启用默认模式签核

    # 启用默认栏位
    cnuser_defualt =fields.Boolean("Enable default",default=False)
    defp_fldname  =fields.Char("Header field name")
    defp_shipfdids =fields.Char("parent ship field name")
    defcd_orcitmid =fields.Char("Submission Old field name")
    defcd_fldname =fields.Char("Submission Status field name")
    defcd_2relstate =fields.Char("Submission State change value")
    
    defcd_version_fldname =fields.Char("Submission Version field name")
    # 匹配值
    defcd_fldnameisversion =fields.Char("Submission judge change version value")
    # 读取需要匹配的栏位，这里是栏位名称
    defcd_newitemid =fields.Char("Submission Status field name")
    defcd_oldstateupda = fields.Char("Submission Old version status change value")

    def _get_reviewers(self):
        """Override to include multiple_individuals review_type."""
        if self.definition_id.review_type == "multiple_individuals":
            # Return the specific reviewer assigned to this review record
            # If specific_reviewer_id is set, return it; otherwise return empty recordset
            return self.specific_reviewer_id or self.env['res.users']
        return super()._get_reviewers()

    @api.model
    def _get_reviewer_fields(self):
        """Override to include reviewer_id and specific_reviewer_id fields for multiple_individuals."""
        fields = super()._get_reviewer_fields()
        # Add reviewer_id and specific_reviewer_id to dependencies
        fields.append("reviewer_id")
        fields.append("specific_reviewer_id")
        return fields

    @api.depends('status', 'definition_id.approve_sequence', 'definition_id.review_type',
                 'definition_id.reviewer_ids', 'definition_id.reviewer_id',
                 'definition_id.reviewer_group_id', 'definition_id.reviewer_field_id',
                 'specific_reviewer_id')
    def _compute_can_review(self):
        """Override to ensure only assigned reviewers can review for all review types."""
        # Process all records with our custom logic
        for rec in self:
            # 只在狀態為 waiting 時根據 sequence 設定初始狀態
            # 狀態為 pending 時不改變狀態，因為它可能已經被 _validate_tier 方法修改
            if rec.status == 'waiting':
                # 根據用戶需求：
                # Sequence = 1 為 pending 狀態
                # Sequence = 2 為 waiting 狀態
                # Sequence = 30X 為 waiting 狀態
                if rec.sequence == 1:
                    rec.status = 'pending'
                elif rec.sequence == 2:
                    rec.status = 'waiting'
                elif rec.sequence >= 300 and rec.sequence < 400:
                    rec.status = 'waiting'
                # 保留原有的其他序列邏輯以保持向後兼容性
                elif rec.sequence == 4:
                    rec.status = 'pending'
                elif rec.sequence >= 200 and rec.sequence < 300:
                    rec.status = 'waiting'
                elif rec.sequence >= 500 and rec.sequence < 600:
                    rec.status = 'waiting'
            
            # Use the new _can_review_value method which has strict checks
            rec.can_review = rec._can_review_value()
            
            # 不再根據 can_review 修改狀態，因為 _can_review_value 方法已經根據狀態返回正確的值
            # 狀態應該只根據 sequence 和業務邏輯設定
            
            _logger.debug("Review %s can_review = %s, status = %s, approve_sequence = %s, user = %s",
                          rec.id, rec.can_review, rec.status, rec.definition_id.approve_sequence, self.env.user.name)

    def _can_review_value(self):
        """Override to ensure only the assigned reviewer can review for all review types."""
        # 狀態為 Waiting 時，任何人都不允許點選 Validate 或 reject 按鈕
        if self.status == "waiting":
            return False
        
        # 狀態為 Pending 時，該關卡的 Todo by 人員可以點選 Validate 或 reject 按鈕，其他人不允許按
        if self.status == "pending":
            # Get reviewers directly from the review record
            reviewers = self._get_reviewers()
            if not reviewers or self.env.user not in reviewers:
                return False
            
            # For multiple_individuals type, also check specific_reviewer_id
            if self.definition_id.review_type == "multiple_individuals":
                if not self.specific_reviewer_id or self.specific_reviewer_id != self.env.user:
                    return False
            
            # Check approve_sequence logic from parent
            if not self.approve_sequence:
                return True
            
            # If approve_sequence is True, check sequence order
            resource = self.env[self.model].browse(self.res_id)
            reviews = resource.review_ids.filtered(lambda r: r.status == "pending")
            if not reviews:
                return True
            sequence = min(reviews.mapped("sequence"))
            return self.sequence == sequence
        
        # 其他狀態（rejected, approved, goback）不允許審核
        return False


class TierValidationInherit(models.AbstractModel):
    _name = "tier.validation"
    _inherit = "tier.validation"
    _description = "Tier Validation (abstract)"
    
    
   
    # 执行modle的方法，若是空值会报错，所有用try
    def execmethod(self,reviews,update_state,methodname):         
        try:
            method_name = methodname
            # 使用getattr来获取方法对象
            method = getattr(self, method_name, None)
            # 检查方法是否存在
            if method and update_state :
                # 调用方法 逻辑处理送审物件-换版，发布
                result = method()
                print(result)  # 输出: Hello from my_method!
            else:
                print(f"Method {method_name} not found.")
        except Exception as e:
             _logger.error("Error in execmethod: %s", str(e))


    

    def setversionflog(self):
        """Default setversionflog method. If model has versionflog field, set it to False."""
        self.ensure_one()
        if hasattr(self, 'versionflog'):
            self.write({"versionflog": False, "create_uid": self.create_uid})
        else:
            # If versionflog field does not exist, do nothing (or log)
            _logger.debug("Model %s has no versionflog field, skipping.", self._name)
    def _prepare_tier_review_vals(self, definition, sequence):
        """Override to create multiple review records for multiple reviewers."""
        if definition.review_type == "multiple_individuals" and definition.reviewer_ids:
            vals_list = []
            for idx, reviewer in enumerate(definition.reviewer_ids):
                # Create a unique sequence per reviewer within the same tier
                sub_sequence = sequence * 100 + idx
                vals = super()._prepare_tier_review_vals(definition, sub_sequence)
                vals.update({
                    'specific_reviewer_id': reviewer.id,
                })
                # 根據 sequence 設定初始狀態
                # 注意：sub_sequence 是 sequence * 100 + idx
                # 所以我們需要檢查原始的 sequence 值來決定狀態
                # 根據用戶需求：
                # Sequence = 1 為 pending 狀態
                # Sequence = 2 為 waiting 狀態
                # Sequence = 30X 為 waiting 狀態
                if sequence == 1:
                    vals['status'] = 'pending'
                elif sequence == 2:
                    vals['status'] = 'waiting'
                elif sequence >= 300 and sequence < 400:
                    vals['status'] = 'waiting'
                # 保留原有的其他序列邏輯以保持向後兼容性
                elif sequence == 4:
                    vals['status'] = 'pending'
                elif sequence >= 200 and sequence < 300:
                    vals['status'] = 'waiting'
                elif sequence >= 500 and sequence < 600:
                    vals['status'] = 'waiting'
                vals_list.append(vals)
            return vals_list
        else:
            vals = super()._prepare_tier_review_vals(definition, sequence)
            # 根據 sequence 設定初始狀態
            # 根據用戶需求：
            # Sequence = 1 為 pending 狀態
            # Sequence = 2 為 waiting 狀態
            # Sequence = 30X 為 waiting 狀態
            if sequence == 1:
                vals['status'] = 'pending'
            elif sequence == 2:
                vals['status'] = 'waiting'
            elif sequence >= 300 and sequence < 400:
                vals['status'] = 'waiting'
            # 保留原有的其他序列邏輯以保持向後兼容性
            elif sequence == 4:
                vals['status'] = 'pending'
            elif sequence >= 200 and sequence < 300:
                vals['status'] = 'waiting'
            elif sequence >= 500 and sequence < 600:
                vals['status'] = 'waiting'
            return vals

    def request_validation(self):
        #签核前先write一次，便于处理flog,重新激活签核
        self.setversionflog()
        td_obj = self.env["tier.definition"]
        tr_obj = self.env["tier.review"]
        vals_list = []
        for rec in self:
            if rec._check_state_from_condition() and rec.need_validation:
                tier_definitions = td_obj.search(
                    [
                        ("model", "=", self._name),
                        ("company_id", "in", [False] + self.env.company.ids),
                    ],
                    order="sequence desc",
                )
                sequence = 0
                for td in tier_definitions:
                    if rec.evaluate_tier(td):
                        sequence += 1
                        vals = rec._prepare_tier_review_vals(td, sequence)
                        if isinstance(vals, list):
                            vals_list.extend(vals)
                        else:
                            vals_list.append(vals)
                self._update_counter({"review_created": True})
        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
        return created_trs



    def validate_tier(self):
        """Override to properly handle multiple_individuals review type with comments."""
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(
            lambda x: x.sequence in sequences or x.approve_sequence_bypass
        )
        
        # For multiple_individuals type, filter reviews where current user is the specific reviewer
        if any(r.definition_id.review_type == "multiple_individuals" for r in reviews):
            reviews = reviews.filtered(
                lambda r: r.definition_id.review_type != "multiple_individuals" or
                         (r.specific_reviewer_id and r.specific_reviewer_id == self.env.user)
            )
        
        if self.has_comment:
            user_reviews = reviews.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            )
            # For multiple_individuals type, also check specific_reviewer_id
            if any(r.definition_id.review_type == "multiple_individuals" for r in user_reviews):
                user_reviews = user_reviews.filtered(
                    lambda r: r.definition_id.review_type != "multiple_individuals" or
                             (r.specific_reviewer_id and r.specific_reviewer_id == self.env.user)
                )
            return self._add_comment("validate", user_reviews)
        
        self._validate_tier(reviews)
        self._update_counter({"review_deleted": True})

    def reject_tier(self):
        """Override to use call_reject_tier which does not require cn.tempselect."""
        return self.call_reject_tier()


        
        
        # if self.has_comment:
        #     return self._add_comment("reject", reviews)
        # self._rejected_tier(reviews)
        # self._update_counter({"review_deleted": True})
    
    def call_reject_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda x: x.sequence in sequences)
        
        # For multiple_individuals type, filter reviews where current user is the specific reviewer
        if any(r.definition_id.review_type == "multiple_individuals" for r in reviews):
            reviews = reviews.filtered(
                lambda r: r.definition_id.review_type != "multiple_individuals" or
                         (r.specific_reviewer_id and r.specific_reviewer_id == self.env.user)
            )
        
        if self.has_comment:
            return self._add_comment("reject", reviews)
        self._rejected_tier(reviews)
        self._update_counter({"review_deleted": True})



    @api.onchange("review_type")
    def onchange_review_type(self):
        super().onchange_review_type()
        if self.review_type != "multiple_individuals":
            self.reviewer_ids = False
        if self.review_type != "individual":
            self.reviewer_id = False
        if self.review_type != "group":
            self.reviewer_group_id = False
        if self.review_type != "field":
            self.reviewer_field_id = False

    def action_on_close(self):
        context = self.env.context

        # 获取选中的记录 ID
        selected_ids = context.get('active_ids', [])


    # 重写方法 _rejected_tier
    def _rejected_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        # reject退回修改 by pmo.ebert 202412
          
        try:
            sequences = self._get_sequences_to_approve(self.env.user)
            reviews = self.review_ids.filtered(
                lambda x: x.sequence in sequences or x.approve_sequence_bypass
            )
            # 检查是否申请人重复提出退回（仅对非多人签核类型进行检查）
            # 如果任何审核记录的review_type为multiple_individuals，则跳过检查
            if not any(rev.definition_id.review_type == "multiple_individuals" for rev in reviews):
                rseq = sequences.copy()
                if rseq:
                    rseq[0] = sequences[0] - 1
                rej_reviews = self.review_ids.filtered(
                    lambda x: x.sequence in rseq or x.approve_sequence_bypass
                )
                if rej_reviews.to_state == reviews.to_state and rej_reviews.name == reviews.name:
                    raise UserError("请不要重复退回！")
                
            self.execmethod(reviews, True, reviews.reject_method)
        except Exception as e:
               if f"{e}" == '请不要重复退回！':
                   raise UserError("请不要重复退回！")
        # reject退回修改 by pmo.ebert 202412
        copyreviewhistorys = self.reject_restart_validation()
        self.reject_request_validation(copyreviewhistorys)

    # 重写方法 restart_validation
    def restart_validation(self):
        # reject退回修改 by pmo.ebert 202412       
        try:          
            sequences = self._get_sequences_to_approve(self.env.user)
            reviews = self.review_ids.filtered(
                lambda x: x.sequence in sequences or x.approve_sequence_bypass
            )
            self.execmethod(reviews,True,reviews.reject_method)            
        except Exception as e:
                a=1
       
       
        for rec in self:
            partners_to_notify_ids = False
            if getattr(rec, self._state_field) in self._state_from:
                to_update_counter = (
                    rec.mapped("review_ids").filtered(
                        lambda a: a.status in ("waiting", "pending")
                    )
                    and True
                    or False
                )
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if reviews_to_notify:
                    partners_to_notify_ids = (
                        reviews_to_notify.mapped("reviewer_ids")
                        .mapped("partner_id")
                        .ids
                    )
                rec.mapped("review_ids").unlink()
              
                if to_update_counter:
                    self._update_counter({"review_deleted": True})
            if partners_to_notify_ids:
                subscribe = "message_subscribe"
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if hasattr(self, subscribe):
                    getattr(self, subscribe)(partner_ids=partners_to_notify_ids)
                rec._notify_restarted_review()

    
    
    def reject_request_validation(self,copyreviewhistorys):
        self.ensure_one()

        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(
            lambda x: x.sequence in sequences or x.approve_sequence_bypass
        )
        

        # root = tk.Tk()
        # root.title("Select Option")
        
        # options = ["Option 1", "Option 2", "Option 3"]  # 动态选项列表
        # selected_option = tk.StringVar()
        
        # ttk.Label(root, text="Please select an option:").pack(pady=10)
        # option_menu = ttk.OptionMenu(root, selected_option, options[0], *options)
        # option_menu.pack()
        
        # def on_close():
        #     selected = selected_option.get()
        #     root.destroy()
        #     return selected
        
        # button = ttk.Button(root, text="Submit", command=on_close)
        # button.pack(pady=20)
        
        # root.protocol("WM_DELETE_WINDOW", on_close)  # 确保点击关闭按钮时调用on_close
        # root.mainloop()
        # return selected_option.get()

        # button = tk.Button(root, text="点击选择", command=show_options)
        # button.pack()
        # root.mainloop()


        td_obj = self.env["tier.definition"]
        tr_obj = self.env["tier.review"]
        vals_list = []
        for rec in self:
            if rec._check_state_from_condition() and rec.need_validation or 1==1:
                tier_definitions = td_obj.search(
                    [
                        ("model", "=", self._name),
                        ("company_id", "in", [False] + self.env.company.ids),
                    ],
                    order="sequence desc",
                )
                # 拒絕後重新生成時，從 sequence = 4 開始
                # 根據用戶需求：拒絕後生成 Sequence = 4 為 pending 狀態，Sequence = 50X 為 Waiting 狀態
                sequence = 4  # 從 4 開始
                for td in tier_definitions:
                    if rec.evaluate_tier(td):
                        # 第一個 tier 使用 sequence = 4
                        # 後續的 tier 使用 sequence = 500, 501, 502 等
                        if sequence == 4:
                            # 第一個 tier 使用 sequence = 4
                            vals = rec._prepare_tier_review_vals(td, sequence)
                            if isinstance(vals, list):
                                vals_list.extend(vals)
                            else:
                                vals_list.append(vals)
                            sequence = 500  # 下一個從 500 開始
                        else:
                            # 後續的 tier 使用 sequence = 500, 501, 502 等
                            vals = rec._prepare_tier_review_vals(td, sequence)
                            if isinstance(vals, list):
                                vals_list.extend(vals)
                            else:
                                vals_list.append(vals)
                            sequence += 1  # 增加 sequence
                self._update_counter({"review_created": True})
        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
        # 根據用戶需求，只有 Sequence = 4 應該是 pending
        # Sequence = 50X 應該是 waiting
        # 所以我們不需要將所有 multiple_individuals 的 waiting 狀態改為 pending
        # 保持原來的狀態設定
        return created_trs
       

    def reject_restart_validation(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        review = self.review_ids.filtered(
            lambda x: x.sequence in sequences or x.approve_sequence_bypass
        )
        review.write({
                        "status": "goback",
                        "can_review": False,
                        "reviewed_date": fields.Datetime.now(),
                        "done_by": self.env.user.id,                            
                    })
        # 保留已经签核的            
        copyreviewhistorys=self.review_ids.filtered(
            lambda x: x.reviewed_date !=False
        )
        for td in copyreviewhistorys:
            td.copy()
        for rec in self:
            partners_to_notify_ids = False
            if getattr(rec, self._state_field) in self._state_from:
                to_update_counter = (
                    rec.mapped("review_ids").filtered(
                        lambda a: a.status in ("waiting", "pending")
                    )
                    and True
                    or False
                )
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if reviews_to_notify:
                    partners_to_notify_ids = (
                        reviews_to_notify.mapped("reviewer_ids")
                        .mapped("partner_id")
                        .ids
                    )
                rec.mapped("review_ids").unlink()
                if to_update_counter:
                    self._update_counter({"review_deleted": True})
            if partners_to_notify_ids:
                subscribe = "message_subscribe"
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if hasattr(self, subscribe):
                    getattr(self, subscribe)(partner_ids=partners_to_notify_ids)
                rec._notify_restarted_review()
        return copyreviewhistorys
    def _get_tier_validation_readonly_domain(self):
        return "bool(review_ids) and state !='New'"
    
    
    # 重新方法显示下一关卡
    def _compute_next_review(self):
        for rec in self:
            review = rec.review_ids.sorted("sequence").filtered(
                lambda x: x.status == "waiting"
            )[:1]
            rec.next_review = review and _("Next: %s") % review.name or "Close"

    # 202503直接修改这个方法，他用于签核，审批意见弹出也调用此方法
    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        
        # For multiple_individuals type, check specific_reviewer_id instead of reviewer_ids
        waiting_reviews = tier_reviews.filtered(
            lambda r: (r.status == "waiting" or r.approve_sequence_bypass)
            and (
                (r.definition_id.review_type == "multiple_individuals" and r.specific_reviewer_id == self.env.user)
                or (r.definition_id.review_type != "multiple_individuals" and self.env.user in r.reviewer_ids)
            )
        )
        if waiting_reviews:
            waiting_reviews.write(
                {
                    "status": "pending",
                }
            )

        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (
                (r.definition_id.review_type == "multiple_individuals" and r.specific_reviewer_id == self.env.user)
                or (r.definition_id.review_type != "multiple_individuals" and self.env.user in r.reviewer_ids)
            )
        )
        user_reviews.write(
            {
                "status": "approved",
                "done_by": self.env.user.id,
                "reviewed_date": fields.Datetime.now(),
            }
        )
        reviews_to_notify = user_reviews.filtered(
            lambda r: r.definition_id.notify_on_accepted
        )
        if reviews_to_notify:
            subscribe = "message_subscribe"
            if hasattr(self, subscribe):
                # For multiple_individuals type, use specific_reviewer_id instead of reviewer_ids
                partner_ids = []
                for review in reviews_to_notify:
                    if review.definition_id.review_type == "multiple_individuals" and review.specific_reviewer_id:
                        partner_ids.append(review.specific_reviewer_id.partner_id.id)
                    else:
                        partner_ids.extend(review.reviewer_ids.mapped("partner_id").ids)
                
                # Remove duplicates
                partner_ids = list(set(partner_ids))
                if partner_ids:
                    getattr(self, subscribe)(partner_ids=partner_ids)
            
            for review in reviews_to_notify:
                rec = self.env[review.model].browse(review.res_id)
                rec._notify_accepted_reviews()

        # Determine which tiers have been fully approved.
        # Group reviews by (definition, original_sequence)
        tier_dict = {}
        for review in self.review_ids:
            key = (review.definition_id, review.sequence // 100)
            tier_dict.setdefault(key, []).append(review)

        # Process each tier that has at least one review just approved (user_reviews)
        processed_tiers = set()
        for review in user_reviews:
            key = (review.definition_id, review.sequence // 100)
            if key in processed_tiers:
                continue
            tier_reviews = tier_dict[key]
            # Check if all reviews in this tier are approved
            if all(r.status == "approved" for r in tier_reviews):
                # All reviewers have approved, proceed with state change and method execution
                self._execute_tier_actions(tier_reviews)
                processed_tiers.add(key)
            else:
                # Not all reviewers have approved yet, do not execute state change
                _logger.debug(
                    "Not all reviewers have approved for tier %s (definition %s, sequence %s).",
                    review.definition_id.name,
                    review.definition_id.id,
                    review.sequence // 100,
                )
        
        # 當一個 review 被批准後，將對應的 waiting reviews 狀態改為 pending
        # 根據用戶需求：
        # 1. 當 Sequence = 1 的 Todo By 人員簽核完成，Sequence = 2 的狀態從 Waiting 改為 Pending
        # 2. Sequence = 30X 保持 Waiting 狀態
        # 3. 保留原有的邏輯以保持向後兼容性
        if user_reviews:
            # 找出被批准的 review 的 sequence
            approved_sequences = user_reviews.mapped("sequence")
            
            # 根據用戶的業務邏輯：
            # - 如果批准的是 Sequence = 1，則 Sequence = 2 從 waiting 改為 pending
            # - Sequence = 30X (300-399) 保持 waiting 狀態
            # - 保留原有的邏輯：Sequence = 20X (200-299) 和 Sequence = 50X (500-599)
            
            for approved_seq in approved_sequences:
                if approved_seq == 1:
                    # Sequence = 1 批准後，Sequence = 2 改為 pending
                    waiting_seq2 = self.review_ids.filtered(
                        lambda r: r.status == "waiting" and r.sequence == 2
                    )
                    if waiting_seq2:
                        waiting_seq2.write({"status": "pending"})
                        _logger.debug("After sequence 1 approved, sequence 2 changed to pending")
                        # 強制觸發 can_review 計算
                        waiting_seq2._compute_can_review()
                    
                    # 保留原有的邏輯：Sequence = 20X (200-299) 改為 pending
                    waiting_20x = self.review_ids.filtered(
                        lambda r: r.status == "waiting" and
                                 r.sequence >= 200 and r.sequence < 300
                    )
                    if waiting_20x:
                        waiting_20x.write({"status": "pending"})
                        _logger.debug("After sequence 1 approved, %s reviews (200-299) changed to pending", len(waiting_20x))
                        # 強制觸發 can_review 計算
                        waiting_20x._compute_can_review()
                
                elif approved_seq == 4:
                    # Sequence = 4 批准後，所有 Sequence = 50X 改為 pending
                    waiting_50x = self.review_ids.filtered(
                        lambda r: r.status == "waiting" and
                                 r.sequence >= 500 and r.sequence < 600
                    )
                    if waiting_50x:
                        waiting_50x.write({"status": "pending"})
                        _logger.debug("After sequence 4 approved, %s reviews (500-599) changed to pending", len(waiting_50x))
                        # 強制觸發 can_review 計算
                        waiting_50x._compute_can_review()
                
                # 對於其他 sequence，不自動改變狀態（保持原來的邏輯）

    def _execute_tier_actions(self, tier_reviews):
        """Execute state change and method for a given tier (or single review)."""
        # Convert tier_reviews to a recordset if it's a list
        if isinstance(tier_reviews, list):
            tier_reviews = self.env['tier.review'].browse([r.id for r in tier_reviews])
        # Ensure we have at least one review
        if not tier_reviews:
            return
        # All reviews belong to the same definition, so we can take the first one
        definition = tier_reviews[0].definition_id
        try:
            domethod = definition.domethod
            to_state = definition.to_state
            update_state = False

            cnuser_defualt = definition.cnuser_defualt
            _logger.debug("Processing record: %s", cnuser_defualt)
            defp_fldname = definition.defp_fldname

            defp_shipfdids = definition.defp_shipfdids
            defcd_orcitmid = definition.defcd_orcitmid
            defcd_fldname = definition.defcd_fldname
            defcd_2relstate = definition.defcd_2relstate
            defcd_newitemid = definition.defcd_newitemid
            defcd_fldnameisversion = definition.defcd_fldnameisversion
            defcd_version_fldname = definition.defcd_version_fldname
            defcd_oldstateupda = definition.defcd_oldstateupda

            # Determine if state should be updated based on any of the reviews
            # Since all reviews have the same to_state, we can use the first one
            if to_state and to_state != self.state:
                update_state = True

            # update 2503 优化段，写入表头和页签的升级
            if cnuser_defualt:
                if to_state and defp_fldname:
                    try:
                        self.write({defp_fldname: to_state, "create_uid": self.create_uid})
                        # 刷新緩存，確保後續方法能讀取到最新的狀態
                        self.refresh()
                    except Exception as e:
                        self.write({defp_fldname: int(to_state), "create_uid": self.create_uid})
                        # 刷新緩存，確保後續方法能讀取到最新的狀態
                        self.refresh()
                else:
                    _logger.error(
                        "Error in my_method: %s",
                        str("请配置签核栏位to_state，defp_fldname"),
                    )
                if defp_shipfdids and defcd_orcitmid and defcd_fldname and defcd_2relstate:
                    for shipitem in self[defp_shipfdids]:
                        record = shipitem[defcd_orcitmid]
                        newrecord = shipitem[defcd_newitemid]
                        # 处理换版
                        if record != False:
                            # 退回后需要判断是否已经换版
                            if (
                                shipitem[defcd_newitemid]
                                and len(shipitem[defcd_newitemid]) != 0
                            ):
                                befor_version = shipitem[defcd_newitemid][defcd_version_fldname]
                                after_version = record[defcd_version_fldname]
                                if after_version == befor_version + 1:
                                    continue

                            if not newrecord and record[defcd_fldname] == defcd_fldnameisversion:
                                # code = str(record.affected_bom_id.version+1)
                                default = {
                                    "active": False,
                                    defcd_version_fldname: record[defcd_version_fldname] + 1,
                                }
                                newitem = record.sudo().copy(default)
                                if record["engineering_code"]:
                                    newitem.update(
                                        {"engineering_code": record["engineering_code"], "create_uid": self.create_uid}
                                    )
                                # newitem[defcd_version_fldname]=record[defcd_version_fldname] + 1

                                record.update({defcd_fldname: defcd_oldstateupda})
                                # record.affected_bom_id.write({'cnis_current':True})
                                shipitem.update(
                                    {defcd_newitemid: newitem.id, "create_uid": self.create_uid}
                                )
                                # self.write({'btnflog': False})

                            elif not newrecord:
                                shipitem.write({defcd_newitemid: record.id})
                                record.update({defcd_fldname: defcd_2relstate, "create_uid": self.create_uid})
                            elif newrecord:
                                newrecord.update({defcd_fldname: defcd_2relstate, "create_uid": self.create_uid})
                                # if   defcd_2relstate == defcd_fldnameisversion and  newrecord[defcd_version_fldname] !=0 :
                                # 用新建版本的送审对象的id来判定是否修改新版的active,旧版的active,状态
                                if record.id != newrecord.id and newrecord[defcd_version_fldname] != 0:
                                    newrecord.update({"active": True})
                                    record.update(
                                        {defcd_fldname: defcd_oldstateupda, "active": False, "create_uid": self.create_uid}
                                    )
            else:
                if to_state and update_state:
                    self.write({"state": to_state, "create_uid": self.create_uid})
                    # 刷新緩存，確保後續方法能讀取到最新的狀態
                    self.refresh()
                    # 执行modle的方法，若是空值会报错，所有用try
                    self.execmethod(tier_reviews, update_state, domethod)
                else:
                    if not to_state:
                        self.execmethod(tier_reviews, True, domethod)
        except Exception as e:
            a = 1
            self.execmethod(tier_reviews, True, domethod)
    
    @api.model
    def _search_validated(self, operator, value):
        """Search method for validated field, handling various operators."""
        # Convert operator to "=" or "!=" if possible
        if operator in ("=", "!="):
            pass
        elif operator == "in" and isinstance(value, list):
            if True in value and False not in value:
                operator = "="
                value = True
            elif False in value and True not in value:
                operator = "="
                value = False
            else:
                # Both True and False, meaning all records match? Return empty domain.
                return []
        elif operator == "not in" and isinstance(value, list):
            if True in value and False not in value:
                operator = "!="
                value = True
            elif False in value and True not in value:
                operator = "!="
                value = False
            else:
                # Both True and False, meaning no records match? Return domain that always false.
                return [("id", "=", 0)]
        else:
            # Unsupported operator, default to "="
            operator = "="
            value = bool(value)
        # Original logic
        pos = self.search([(self._state_field, "in", self._state_from)]).filtered(
            lambda r: r.validated
        )
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", pos.ids)]
        else:
            return [("id", "not in", pos.ids)]

    @api.model
    def _search_rejected(self, operator, value):
        """Search method for rejected field, handling various operators."""
        # Convert operator to "=" or "!=" if possible
        if operator in ("=", "!="):
            pass
        elif operator == "in" and isinstance(value, list):
            if True in value and False not in value:
                operator = "="
                value = True
            elif False in value and True not in value:
                operator = "="
                value = False
            else:
                # Both True and False, meaning all records match? Return empty domain.
                return []
        elif operator == "not in" and isinstance(value, list):
            if True in value and False not in value:
                operator = "!="
                value = True
            elif False in value and True not in value:
                operator = "!="
                value = False
            else:
                # Both True and False, meaning no records match? Return domain that always false.
                return [("id", "=", 0)]
        else:
            # Unsupported operator, default to "="
            operator = "="
            value = bool(value)
        # Original logic
        pos = self.search([(self._state_field, "in", self._state_from)]).filtered(
            lambda r: r.rejected
        )
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("id", "in", pos.ids)]
        else:
            return [("id", "not in", pos.ids)]

    # 优化改变变更后审核的控制方法，统一在签核这块写，引用模型只需要添加属性versionflog即可，
    # 这里需要统一属性变量，就是送审
    # def setversionflog(self):
    #     self.ensure_one()
    #     sequences = self._get_sequences_to_approve(self.env.user)
    #     reviews = self.review_ids.filtered(
    #         lambda x: x.sequence in sequences or x.approve_sequence_bypass
    #     )

    #     cnuser_defualt = reviews.definition_id.cnuser_defualt
    #     defp_fldname  = reviews.definition_id.defp_fldname

    #     defp_shipfdids = reviews.definition_id.defp_shipfdids
    #     defcd_orcitmid = reviews.definition_id.defcd_orcitmid
    #     defcd_fldname = reviews.definition_id.defcd_fldname
    #     if defp_shipfdids and defcd_orcitmid and defcd_fldname :
    #                 for shipitem in self[defp_shipfdids]:
    #                     relitem = shipitem[defcd_orcitmid]
    #                     if relitem[defcd_fldname] =="released" :
    #                         versionflog= False  
    #                         self.write({"versionflog":versionflog,"create_uid":self.create_uid})
                        # relitem.update({defcd_fldname:defcd_2relstate,"create_uid":self.create_uid})
        # else :
        #     _logger.error("Error in setversionflog: %s", str("请配置签核栏位defp_shipfdids,defcd_orcitmid"))
                
