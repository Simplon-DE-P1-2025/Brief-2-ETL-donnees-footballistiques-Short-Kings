def clean_percentage(x):
    if isinstance(x, str):
        return float(x.replace('%', ''))
    return x



def clean_round_name(r_raw):
    """
    Normalise les noms des étapes de la compétition (Group Stage, Final, etc.)
    """
    r = str(r_raw).upper().strip()
    
    if 'PRELIMINARY' in r or 'FIRST' in r: return 'Preliminary'
    if 'GROUP' in r: return 'Group Stage'
    if '1/8' in r or 'ROUND OF 16' in r: return 'Round of 16'
    if '1/4' in r or 'QUARTER' in r: return 'Quarter-finals'
    if '1/2' in r or 'SEMI' in r: return 'Semi-final'
    if '3RD' in r or 'THIRD' in r or 'PLAY-OFF' in r: return 'Third Place'
    if 'FINAL' in r: return 'Final'
    
    return r_raw