import json , re
import conf as c

def clean_name(stringa):
    #clean_stringa = s_strip(stringa.replace(r"\(.*\)","")) if stringa != '' and stringa != 'None' else ''
    clean_stringa = s_strip(stringa)
    return clean_stringa

def expand_viaf(stringa):
    stringa = s_strip("http://viaf.org/viaf/"+stringa) if (stringa != '' and stringa != "None") else ''
    return stringa

def s_strip(stringa):
    stringa = stringa.strip() if stringa != '' else ''
    return stringa

def split_values(stringa):
    if stringa != '' and stringa is not None and stringa != 'None' and ';' in stringa:
        values = stringa.split(';')
        values = [s_strip(val) for val in values]
        #print("values",values)
        return values
    elif stringa != '' and stringa is not None and stringa != 'None' and ';' not in stringa:
        return stringa
    else:
        return ''

def date(stringa):
    # TODO validation rules
    if len(s_strip(stringa)) != 0 and stringa is not None:
        return s_strip(stringa)
    else:
        return ''

def vocabulary(stringa,vocab):
    with open(c.VOCABULARIES_INDEX) as json_file:
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
            if data_row["Work title"] is not None:
                name += clean_name(data_row["Work title"])
        if data_row["Event type"] == "Education":
            name += ' studied at '
            if data_row["Organisation or POI"] is not None:
                name += clean_name(data_row["Organisation or POI"])
        if data_row["Event type"] == "Award":
            name += ' awarded by '
            if data_row["Organisation or POI"] is not None:
                name += clean_name(data_row["Organisation or POI"])
        if data_row["Event type"] == "Residence":
            name += ' resident in'

        if len(data_row["City"]) > 2:
            name += ' '+data_row["City"]
        if len(data_row["District"]) > 2:
            name += ', '+data_row["District"]
        if len(data_row["Country"]) > 2:
            name += ', '+data_row["Country"]
        # if (data_row["City"] is None or data_row["City"] == '""') \
        #     and (data_row["Country"] is not None and data_row["Country"] != '""'):
        #     name += ', '+data_row["Country"]
        if len(data_row["From year"]) > 2 or len(data_row["To year"]) > 2:
            from_y = data_row["From year"]
            to_y = data_row["To year"]
            name += ' ('+from_y+'-'+to_y+')'
        if len(data_row["From date"]) > 2 or len(data_row["To date"]) > 2:
            from_y = data_row["From date"]
            to_y = data_row["To date"] 
            name += ' ('+from_y+'-'+to_y+')'

    return name
