def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min) * (old_val - old_min) / (old_max - old_min) + new_min
