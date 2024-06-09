from ._flatten import flatten
from ._unflatten import unflatten


def npop(input_, / ,indices, seperator="|", default=...):
    indices = (
        indices
        if not isinstance(indices, list)
        else seperator.join([str(i) for i in indices])
    )
    
    flatten(input_, inplace=True)

    try:
        out_ = input_.pop(indices, default) if default != ... else input_.pop(indices)
    except KeyError as e:
        if default == ...:
            raise KeyError(f"Key {indices} not found in metadata.") from e
        return default
    
    unflatten(input_, inplace=True)
    return out_