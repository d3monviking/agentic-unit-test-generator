def contains_sublist(main_list, sub_list):
    if not sub_list:
        return True
    if len(sub_list) > len(main_list):
        return False
    for i in range(len(main_list) - len(sub_list) + 1):
        if main_list[i:i+len(sub_list)] == sub_list:
            return True
    return False