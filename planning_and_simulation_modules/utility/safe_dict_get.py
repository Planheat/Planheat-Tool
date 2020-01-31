def get_data(key, data, default=None):
    try:
        return data[key]
    except Exception:
        return default