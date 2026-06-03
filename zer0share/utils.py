"""
通用工具模块。

与业务无关的辅助函数和装饰器。
"""

import functools
import time

import pandas as pd


def paginate(limit: int = 50000, interval: float = 0.05):
    """Tushare offset 分页装饰器。

    不需要知道接口的单次返回上限——每次调用后根据实际返回行数自动累加 offset，
    返回空或行数不足 limit 时自动停止。

    逻辑::

        offset = 0
        while True:
            调用 API(offset=offset, limit=limit)
            if 返回空 → 停止
            累加 df 到结果列表
            offset += len(df)
            sleep(interval)

    Args:
        limit: 单次请求条数，设一个大于任何接口实际上限的安全值即可，默认 50000。
        interval: 每次请求间隔（秒），默认 0.05。免费账户建议不小于 0.3。

    用法::

        @paginate()
        def fetch_xxx(self, ...):
            return self._pro.xxx(...)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:
            all_data = []
            offset = 0

            while True:
                kwargs["offset"] = offset
                kwargs["limit"] = limit

                df = func(*args, **kwargs)
                if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                    break

                all_data.append(df)
                offset += len(df)
                time.sleep(interval)

            if not all_data:
                return pd.DataFrame()
            return pd.concat(all_data, ignore_index=True)

        return wrapper
    return decorator
