def min_cost_path(cost, m, n):
    # Create a table to store results of subproblems
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill dp[][] in bottom-up manner
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 and j == 0:
                dp[i][j] = cost[i][j]
            elif i == 0:
                dp[i][j] = dp[i][j - 1] + cost[i][j]
            elif j == 0:
                dp[i][j] = dp[i - 1][j] + cost[i][j]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + cost[i][j]

    return dp[m][n]