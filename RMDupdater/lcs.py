import time

def by_LCS(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[list()] * (n + 1) for _ in range(m + 1)]
    st = time.time()
    for i in range(1, m+1):
        for j in range(1, n+1):
            if X[i-1] == Y[j-1]:
                C[i][j] = [i-1, ]
                C[i][j].extend(C[i-1][j-1])
            else:
                C[i][j] = (max(C[i-1][j], C[i][j-1], key=len))
    with open('time_log.txt', 'a+') as log:
        log.write("LCS: " + str(st-time.time()) + "\n")
    return C

def by_sort(x, y):
    x.sort()
    y.sort()
    res = list()
    st = time.time()
    for i in range(0, len(x)):
        for j in range(0, len(y)):
            if x[i] == y[j]:
                res.append(i)
                break
            elif x[i] < y[j]:
                break
    with open('time_log.txt', 'a+') as log:
        log.write("SORT: " + str(st-time.time()) + "\n")
    return res

# X = ['hello ', 'my ', 'dear ', 'friend, ', 'I`m ', 'Julia.']
# Y = ['my ', 'dear ', 'friend, ', 'hello!']
#
# m = len(X)
# n = len(Y)
# C = by_LCS(X, Y)
# res = C[m][n]
# for i in res:
#     print(X[i])
#
# st = time.time()
# res = by_sort(X, Y)
# for i in res:
#     print(X[i])
