import heapq

def largest_numbers(nums, k):
    """
    Return the k largest integers from the list nums using a heap queue algorithm.

    Args:
        nums (list): List of integers.
        k (int): Number of largest elements to return.

    Returns:
        list: The k largest integers in descending order.
    """
    if k <= 0:
        return []
    if k >= len(nums):
        return sorted(nums, reverse=True)
    
    # Use a min-heap of size k to keep track of the k largest elements
    heap = nums[:k]
    heapq.heapify(heap)
    
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    
    # Return the heap elements sorted in descending order
    return sorted(heap, reverse=True)