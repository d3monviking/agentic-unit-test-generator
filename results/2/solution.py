def find_similar_elements(list1, list2):
    """
    Finds the similar elements from two tuple lists.

    Args:
        list1 (list of tuples): The first list of tuples.
        list2 (list of tuples): The second list of tuples.

    Returns:
        list: A list of tuples that are present in both list1 and list2.
    """
    set1 = set(list1)
    set2 = set(list2)
    similar_elements = list(set1.intersection(set2))
    return similar_elements