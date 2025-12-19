
def clean_percentage(x):
    if isinstance(x, str):
        return float(x.replace('%', ''))
    return x