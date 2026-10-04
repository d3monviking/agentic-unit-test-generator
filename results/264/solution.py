def dog_years(human_years):
    if human_years <= 0:
        return 0
    elif human_years == 1:
        return 15
    elif human_years == 2:
        return 24
    else:
        return 24 + (human_years - 2) * 5