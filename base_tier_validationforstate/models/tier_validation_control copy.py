# Copyright 2017 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools.misc import frozendict

class TierDefinition(models.Model):
    _name = "tier.definition"
    _inherit = "tier.definition"
    _description = "Tier Definition"

    to_state = fields.Char(string="to state")
    domethod = fields.Char(string="used method")

    # reject_state_parent = fields.Char(string="parent reject state")
    # reject_state_child = fields.Char(string="child reject state")
    reject_method = fields.Char(string="reject method")

    

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
    to_state = fields.Char(related="definition_id.to_state", readonly=True)
    domethod = fields.Char(related="definition_id.domethod", readonly=True)

    # reject_state_parent = fields.Char(related="definition_id.reject_state_parent", readonly=True)
    # reject_state_child = fields.Char(related="definition_id.reject_state_child", readonly=True)

    reject_method = fields.Char(related="definition_id.reject_method", readonly=True)


class TierValidationInherit(models.AbstractModel):
    _name = "tier.validation"
    _inherit = "tier.validation"
    _description = "Tier Validation (abstract)"
    
    
    def validate_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(
            lambda x: x.sequence in sequences or x.approve_sequence_bypass
        )
        if self.has_comment:
            user_reviews = reviews.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            )
            return self._add_comment("validate", user_reviews)
        self._validate_tier(reviews)
        self._update_counter({"review_deleted": True})
        domethod=""
        to_state=""
        update_state=False
        
        try:
            if reviews.to_state != self.state:
                update_state=True
            if reviews.to_state and update_state :
                to_state = reviews.to_state
                self.update({"state":to_state,"create_uid":self.create_uid})
                # 执行modle的方法，若是空值会报错，所有用try
                self.execmethod(reviews,update_state,reviews.domethod)
            else :
                if  not reviews.to_state :
                    self.execmethod(reviews,True,reviews.domethod)
        except Exception as e:
                a=1
                self.execmethod(reviews,True,reviews.domethod)    

        # 优化项，可采用默认送审物件改变状态，目前还
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
            a=1
       

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
                        vals_list.append(rec._prepare_tier_review_vals(td, sequence))
                self._update_counter({"review_created": True})
        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
        return created_trs

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
            # 检查是否申请人重复提出退回
            rseq=  sequences
            rseq[0]=sequences[0]-1
            rej_reviews = self.review_ids.filtered(
                lambda x: x.sequence in rseq or x.approve_sequence_bypass
            )
            if rej_reviews.to_state ==reviews.to_state and rej_reviews.name ==reviews.name :
                raise UserError("请不要重复退回！")
                
            self.execmethod(reviews,True,reviews.reject_method)            
        except Exception as e:
               if f"{e}" =='请不要重复退回！' :
                   raise UserError("请不要重复退回！")
        # reject退回修改 by pmo.ebert 202412      
        copyreviewhistorys=self.reject_restart_validation()        
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
                sequence = len(copyreviewhistorys)
                for td in tier_definitions:
                    if rec.evaluate_tier(td):
                        sequence += 1
                        vals_list.append(rec._prepare_tier_review_vals(td, sequence))
                self._update_counter({"review_created": True})
        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
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
