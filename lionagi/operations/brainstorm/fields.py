from lion_core.operative.fields.models import FieldModel

TOPIC_FIELD = FieldModel(
    default_factory=str,
    description="**Specify the topic or theme for the brainstorming session.**",
    title="Topic",
)

IDEAS_FIELD = FieldModel(
    default_factory=list,
    description="**Provide a list of ideas needed to accomplish the objective. Each step should be as described in a `StepModel`.**",
    title="Ideas",
)
