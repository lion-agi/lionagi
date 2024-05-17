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

#     async def direct(
#         self,
#         directive: str,
#         context=None,
#         instruction=None,
#         confidence_score=None,
#         reason=False,  # for directive
#         branch=None,
#         rulebook=None,
#         imodel=None,
#         num_step=None,
#         return_branch=False,
#         directive_obj=None,
#         directive_params={},
#         directive_kwargs={},
#         **kwargs,
#     ):
#         branch = branch or self.branch
#         out_form, branch = await self.plan(
#             confidence_score=confidence_score,
#             reason=reason,
#             num_step=num_step,
#             imodel=imodel,
#             context=context,
#             branch=branch,
#             instruction=instruction,
#             return_branch=True,
#         )

#         plan = out_form.plan
#         plan = [plan] if isinstance(plan, dict) else plan

#         directive_params["rulebook"] = rulebook or directive_params.get(
#             "rulebook", None
#         )

#         if not directive_obj:
#             if isinstance(directive, str):
#                 directive = UNIT_DIRECTIVE_MAPPING.get(strip_lower(directive), Predict)
#             if not issubclass(directive, Directive):
#                 raise ValueError(
#                     f"directive must be a subclass of BaseDirective, got {type(directive)}"
#                 )

#         directive_obj = directive_obj or directive(branch=branch, **directive_params)

#         directive_kwargs = {**directive_kwargs, **kwargs}
#         directive_kwargs["reason"] = reason or directive_kwargs.get("reason", None)
#         directive_kwargs["confidence_score"] = confidence_score or directive_kwargs.get(
#             "confidence_score", None
#         )

#         chain_forms = []
#         for idx in range(len(plan)):
#             _form = await directive_obj.direct(
#                 instruction=plan[f"step_{idx+1}"], **directive_kwargs
#             )
#             chain_forms.append(_form)

#         out_form.add_field("chain_forms", list, None, chain_forms)

#         reasons = {}
#         confidence_scores = []
#         for idx, item in enumerate(chain_forms):
#             reasons[f"step_{idx+1}"] = getattr(item, "reason", "N/A")
#             confidence_scores.append(getattr(item, "confidence_score", 0))

#         if reasons:
#             setattr(out_form, "chain_reasons", reasons)

#         if sum(confidence_scores) > 0:
#             setattr(
#                 out_form,
#                 "chain_confidence_score",
#                 sum(confidence_scores) / len(chain_forms),
#             )

#         if return_branch:
#             return out_form, branch

#         return out_form
