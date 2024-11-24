def levenshtein_ratio(str1, str2):
    """
    计算两个字符串之间的 Levenshtein 距离比例
    :param str1: 第一个字符串
    :param str2: 第二个字符串
    :return: 相似度得分（0-100）
    """
    len1, len2 = len(str1), len(str2)

    # 创建二维矩阵
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # 初始化矩阵的第一行和第一列
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    # 填充矩阵
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    # 计算相似度比例
    max_len = max(len1, len2)
    return (1 - dp[len1][len2] / max_len) * 100
