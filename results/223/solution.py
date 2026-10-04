def has_majority_element(arr):
    n = len(arr)
    if n == 0:
        return False
    candidate = arr[n // 2]
    left = 0
    right = n - 1
    first_occurrence = n
    last_occurrence = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == candidate:
            first_occurrence = mid
            right = mid - 1
        elif arr[mid] < candidate:
            left = mid + 1
        else:
            right = mid - 1
    left = 0
    right = n - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == candidate:
            last_occurrence = mid
            left = mid + 1
        elif arr[mid] < candidate:
            left = mid + 1
        else:
            right = mid - 1
    count = last_occurrence - first_occurrence + 1
    return count > n // 2