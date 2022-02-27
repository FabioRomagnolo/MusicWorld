import re


def simplify_research(query):
    query = query.lower()
    # Removing phrases inside brackets []
    query = re.sub(r"\[[^\[\]]*\]", "", query)
    # query = re.sub(r"\([^()]*\)", "", query)
    # Removing 'Remastered year' pattern
    query = re.sub(r'((remastered|remaster) [0-9]+)+', "", query)
    query = re.sub(r'([0-9]+ (remastered|remaster))+', "", query)

    # Removing useless words
    to_replace = ['single version', 'remastered', 'remaster', 'remix', 'remixed',
                  'version', 'deluxe', 'extended', '-', 'edition', ';', ':']
    for word in to_replace:
        query = query.replace(word, '')
    # Removing empty brackets
    query = query.replace("()", "")
    query = query.replace("[]", "")
    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def simplify_more_research(query):
    # ATTENTION! The use of this simplification of research is suggested only as last chance
    query = simplify_research(query)
    # Removing phrases inside brackets ()
    query = re.sub(r"\([^()]*\)", "", query)
    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def verify_result(query, result):
    query, result = query.lower(), result.lower()
    for word in re.findall(r'\w+', query):
        if word in re.findall(r'\w+', result):
            return True
    return False
