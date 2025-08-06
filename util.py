def uses_taxi(legs):
    for leg in legs:
        if leg['mode'] == 'ODM':
            return True
    return False