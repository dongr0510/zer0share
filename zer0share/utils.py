"""
通用工具模块。

与业务无关的辅助函数和装饰器。
"""

import functools
import time

import pandas as pd


def paginate(limit: int | None = 50000, interval: float = 0.05):
    """Tushare offset 分页装饰器。

    每次调用后根据实际返回行数自动累加 offset，返回空时停止。
    不需要知道接口的单次返回上限。

    逻辑::

        offset = 0
        while True:
            调用 API(offset=offset, [limit=limit])   # limit 为 None 时不传
            if 返回空 → 停止
            offset += len(df)
            sleep(interval)

    Args:
        limit: 单次请求条数上限，默认 50000。传 None 表示不传 limit 参数
               （部分 Tushare 接口如 index_weight 不支持 limit，只支持 offset）。
        interval: 每次请求间隔（秒），默认 0.05。免费账户建议不小于 0.3。

    用法::

        # 支持 offset + limit 的接口
        @paginate()
        def fetch_stock_basic(self, ...):
            return self._pro.stock_basic(...)

        # 只支持 offset、不支持 limit 的接口
        @paginate(limit=None)
        def fetch_index_weight(self, trade_date, ...):
            return self._pro.index_weight(...)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:
            all_data = []
            offset = 0

            while True:
                kwargs["offset"] = offset
                if limit is not None:
                    kwargs["limit"] = limit

                df = func(*args, **kwargs)
                if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                    print(f"[paginate] offset={offset}: 返回空，分页结束")
                    break

                fetched = len(df)
                offset += fetched
                print(f"[paginate] offset={offset - fetched}, limit={limit} → 返回 {fetched} 条, next offset={offset}")

                # limit 为 None 时无法提前判断最后一页，只能靠返回空来停止
                if limit is not None and fetched < limit:
                    print(f"[paginate] fetched({fetched}) < limit({limit})，分页结束")
                    break

                time.sleep(interval)

            if not all_data:
                return pd.DataFrame()
            return pd.concat(all_data, ignore_index=True)

        return wrapper
    return decorator
