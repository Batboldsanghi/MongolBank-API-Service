def remove_duplicate(data):
    d1 = []
    
    for x in data:
        if(x not in d1):
            d1.append(x)
    
    return d1