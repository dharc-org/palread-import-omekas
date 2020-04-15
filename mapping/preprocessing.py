import json
def clean_name(stringa):
    #clean_stringa = s_strip(stringa.replace(r"\(.*\)","")) if stringa != '' and stringa != 'None' else ''
    clean_stringa = s_strip(stringa)
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

def date(stringa):
    # TODO validation rules
    if len(s_strip(stringa)) != 0 and stringa is not None:
        return s_strip(stringa)
    else:
        return ''

def vocabulary(stringa,vocab):
    with open("vocabularies.json") as json_file:
        vocabularies = json.load(json_file)

    term_URI = [iri for voc,terms in vocabularies.items() for term,iri in terms.items() if term == stringa and voc == vocab]
    term_URI = term_URI[0] if len(term_URI) != 0 else ''
    return term_URI

def create_name(data_row,entity):
    # this is possibly the only function that cannot be reused outside PalREAD
    name = ''
    if entity == "life_event":
        pers = clean_name(data_row["Person  name @ar"]) if (data_row["Person  name @ar"] is not None and data_row["Person  name @ar"] != '') else clean_name(data_row["Person name @en"])
        name += pers+','
        if data_row["Event type"] == "Membership":
            name += ' member of '
            if data_row["Organisation or POI"] is not None:
                name += clean_name(data_row["Organisation or POI"])+'.'
        if data_row["Event type"] == "Employment":
            name += ' employed at '
            if data_row["Organisation or POI"] is not None:
                name += clean_name(data_row["Organisation or POI"])
        if data_row["Event type"] == "Education":
            name += ' studied at '
            if data_row["Organisation or POI"] is not None:
                name += clean_name(data_row["Organisation or POI"])
        if data_row["Event type"] == "Residence":
            name += ' resident in'

        if data_row["City"] != '' and data_row["City"] is not None:
            name += ' '+data_row["City"]
        if data_row["District"] != '':
            name += ', '+data_row["District"]
            if data_row["Country"] != '':
                name += ', '+data_row["Country"]
        if (data_row["City"] is None or data_row["City"] == '') \
            and (data_row["Country"] is not None and data_row["Country"] != ''):
            name += ', '+data_row["Country"]
        if (data_row["From year"] is not None and data_row["From year"] != '') \
            or (data_row["To year"] is not None and data_row["To year"] != ''):
            from_y = data_row["From year"] if data_row["From year"] is not None and data_row["From year"] != '' else ''
            to_y = data_row["To year"] if data_row["To year"] is not None and data_row["To year"] != '' else ''
            name += ' ('+from_y+'-'+to_y+')'
        if (data_row["From date"] is not None and data_row["From date"] != '') \
            or (data_row["To date"] is not None or data_row["To date"] != ''):
            from_y = data_row["From date"] if data_row["From date"] != '' else ''
            to_y = data_row["To date"] if data_row["To date"] != '' else ''
            name += ' ('+from_y+'-'+to_y+')'

    return name
