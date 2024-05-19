# from lionagi.libs.ln_convert import to_list
# from lionagi.libs.ln_convert import strip_lower


# class Chain(Plan):

#     async def chain_of_act(
#         self,
#         context=None,
#         instruction=None,
#         confidence_score=None,
#         return_branch=False,
#         rulebook=None,
#         branch=None,
#         imodel=None,
#         num_step=None,
#         plan_params={},
#         plan_kwargs={},
#     ):

#         branch = branch or self.branch
#         cot = Chain(branch=branch)

#         cot_form, branch = await cot._chain(
#             context=context,
#             instruction=instruction,
#             confidence_score=confidence_score,
#             rulebook=rulebook,
#             imodel=imodel,
#             num_step=num_step,
#             plan_params=plan_params,
#             plan_kwargs=plan_kwargs,
#             return_branch=True,
#             reason=True,
#             directive_obj=self,
#         )

#         act_forms = cot_form.chain_forms
#         fields = ["answer", "reason", "actions", "action_response"]
#         for i in fields:
#             _v = [getattr(j, i, None) for j in act_forms]
#             _v = to_list(_v, flatten=True, dropna=True)
#             _v = " ".join(_v) if i in ["answer", "reason"] else _v
#             cot_form._add_field(
#                 field=f"chain_{i}", annotation=list, default=None, value=_v
#             )

#         if return_branch:
#             return cot_form, branch

#         return cot_form

#     async def chain_of_thoughts(self, context=None, instruction=None, **kwargs):

#         kwargs["directive"] = "predict"
#         return await self.direct(instruction=instruction, context=context, **kwargs)

