def change_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)
