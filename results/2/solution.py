def find_similar_elements(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    return tuple(set1 & set2)