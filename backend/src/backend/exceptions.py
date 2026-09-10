# 複数の機能で共有する業務例外。HTTP応答への変換はルーター側で行う。

class SortOrderIsOutOfRangeError(Exception):
    pass