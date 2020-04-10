def clean_name(stringa):
    clean_stringa = s_strip(stringa.replace(r"\(.*\)","")) if stringa != '' and stringa != 'None' else ''
    return clean_stringa

def expand_viaf(stringa):
    stringa = s_strip("http://viaf.org/viaf/"+stringa) if stringa != '' else ''
    return stringa

def s_strip(stringa):
    stringa = stringa.strip() if stringa != '' else ''
    return stringa

def split_values(stringa):
    if stringa != '' and stringa is not None and stringa != 'None' and ';' in stringa:
        values = stringa.split(';')
        values = [s_strip(val) for val in values]
        return values
    elif stringa != '' and stringa is not None and stringa != 'None' and ';' not in stringa:
        return [stringa]
    else:
        return ''
