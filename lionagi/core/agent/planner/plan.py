# TODO

# class Plan(UnitDirective):
#     defalut_template = PlanTemplate

#     async def direct(
#         self,
#         form=None,
#         num_step=None,
#         reason=False,
#         confidence_score=None,
#         instruction=None,
#         context=None,
#         branch=None,
#         system=None,
#         **kwargs,
#     ):

#         branch = branch or Branch(system=system)

#         if not form:
#             form = self.default_template(
#                 instruction=instruction,
#                 context=context,
#                 num_step=num_step,
#                 reason=reason,
#                 confidence_score=confidence_score,
#             )

#         directive = Chat(branch)
#         return await directive.direct(form=form, **kwargs)

#     async def plan(self, *args, **kwargs):
#         return await self.direct(*args, **kwargs)
