from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from utils.db_func import *
from utils.sql_func import *
from utils.helper import read_sec_list
from utils.visualization import candle_stick, candle_stick_daily

conn = connect_to_db()
# candle_stick("TSLA", 20210318, 20210319)
# candle_stick_daily("TSLA", start_date = 20200912, end_date = 20210225)
valid_dates = get_valid_dates(conn,
                              date_from=int((datetime.now() - timedelta(days=720)).strftime("%Y%m%d")),
                              date_until=int(datetime.now().strftime("%Y%m%d")))


# def three_plus_one_bin(conn, sec_symbol: str, date_key_int: int, valid_dates: list) -> bool:
#     try:
#         idx_ori = valid_dates.index(date_key_int)
#     except Exception as e:
#         print(f"date {date_key_int} does not exist in valid dates")
#         return False
#
#     idx_d1 = idx_ori - 30
#     daily_data = download_data_daily(conn,
#                                      security_symbol=sec_symbol,
#                                      start_date=valid_dates[idx_d1],
#                                      end_date=date_key_int,
#                                      interval="daily")
#     d1_high = daily_data['high_price'].iloc[0:10].max()
#     d2_high = daily_data['high_price'].iloc[10:20].max()
#     d3_high = daily_data['high_price'].iloc[20:30].max()
#
#     d1_low = daily_data['low_price'].iloc[0:10].min()
#     d2_low = daily_data['low_price'].iloc[10:20].min()
#     d3_low = daily_data['low_price'].iloc[20:30].min()
#     print(d1_high, d2_high, d3_high, d1_low, d2_low, d3_low)
#     result = d1_high < d2_high < d3_high and d1_low < d2_low < d3_low
#     return result


# def three_plus_one_bin_slice(conn, sec_symbol: str, date_key_int: int, valid_dates: list, slice_size: int) -> bool:
#     try:
#         idx_ori = valid_dates.index(date_key_int)
#     except Exception as e:
#         print(f"date {date_key_int} does not exist in valid dates")
#         return False
#
#     idx_d1 = idx_ori - 3 * slice_size
#     #     print(valid_dates[idx_d1])
#     daily_data = download_data_daily(conn,
#                                      security_symbol=sec_symbol,
#                                      start_date=valid_dates[idx_d1],
#                                      end_date=date_key_int,
#                                      interval="daily")
#     #     print(daily_data)
#     d1_high = daily_data['high_price'].iloc[0:slice_size].max()
#     d2_high = daily_data['high_price'].iloc[slice_size:2 * slice_size].max()
#     d3_high = daily_data['high_price'].iloc[2 * slice_size:3 * slice_size].max()
#
#     d1_low = daily_data['low_price'].iloc[0:slice_size].min()
#     d2_low = daily_data['low_price'].iloc[slice_size:2 * slice_size].min()
#     d3_low = daily_data['low_price'].iloc[2 * slice_size:3 * slice_size].min()
#     #     print(d1_high, d2_high, d3_high, d1_low, d2_low, d3_low)
#     result = d1_high < d2_high < d3_high and d1_low < d2_low < d3_low
#     return result


def three_plus_one_bin_slice(daily_data, date_key_int: int, slice_size: int) -> bool:
    try:
        idx = daily_data[daily_data['date_int_key'] == date_key_int].index.tolist()[0]
    except Exception as e:
        return False
    d3_high = daily_data['high_price'].iloc[idx - slice_size:idx].max()
    d2_high = daily_data['high_price'].iloc[idx - 2 * slice_size:idx - slice_size].max()
    d1_high = daily_data['high_price'].iloc[idx - 3 * slice_size:idx - 2 * slice_size].max()

    d3_low = daily_data['low_price'].iloc[idx - slice_size:idx].min()
    d2_low = daily_data['low_price'].iloc[idx - 2 * slice_size:idx - slice_size].min()
    d1_low = daily_data['low_price'].iloc[idx - 3 * slice_size:idx - 2 * slice_size].min()
    result = d1_high < d2_high < d3_high and d1_low < d2_low < d3_low
    return result


# def three_plus_one_return(conn, sec_symbol: str, date_key_int: int, valid_dates: list) -> float:
#     try:
#         idx_ori = valid_dates.index(date_key_int)
#     except Exception as e:
#         print(f"date {date_key_int} does not exist in valid dates")
#         return 0
#
#     idx_d4 = idx_ori + 10
#     if len(valid_dates) <= idx_d4:
#         print("date is too recent")
#         return 0
#
#     daily_data = download_data_daily(conn,
#                                      security_symbol=sec_symbol,
#                                      start_date=date_key_int,
#                                      end_date=valid_dates[idx_d4],
#                                      interval="daily")
#     return log_return(daily_data['close_price'].iloc[0], daily_data['close_price'].iloc[-1])

def three_plus_one_return(daily_data, date_key_int: int, slice_size: int) -> bool:
    idx = daily_data[daily_data['date_int_key'] == date_key_int].index.tolist()[0]
    return log_return(daily_data['close_price'].iloc[idx], daily_data['close_price'].iloc[idx+slice_size])

def log_return(a: float, b: float) -> float:
    return np.log(b/a)


# def validate_three_plus_one(conn, sec_symbol: str,
#                             start_date_int: int,
#                             end_date_int: int,
#                             valid_dates: list,
#                             slice_size: int):
#     try:
#         st_idx = valid_dates.index(start_date_int)
#         ed_idx = valid_dates.index(end_date_int)
#     except Exception as e:
#         print(f"date {start_date_int} or {end_date_int} does not exist in valid dates")
#         return False
#
#     res = list()
#     for idx in range(st_idx, ed_idx):
#         test_date = valid_dates[idx]
#         criteria = three_plus_one_bin_slice(conn,
#                                             sec_symbol=sec_symbol,
#                                             date_key_int=test_date,
#                                             valid_dates=valid_dates,
#                                             slice_size=slice_size)
#         if criteria:
#             result = three_plus_one_return(conn,
#                                            sec_symbol=sec_symbol,
#                                            date_key_int=test_date,
#                                            valid_dates=valid_dates)
#             res.append(result)
#     return res


def validate_three_plus_one_op(conn, sec_symbol: str,
                               start_date_int: int,
                               end_date_int: int,
                               valid_dates: list,
                               slice_size: int):
    try:
        st_idx = valid_dates.index(start_date_int)
        ed_idx = valid_dates.index(end_date_int)
    except Exception as e:
        print(f"date {start_date_int} or {end_date_int} does not exist in valid dates")
        return False

    daily_data = download_data_daily(conn,
                                     security_symbol=sec_symbol,
                                     start_date=valid_dates[st_idx - 3 * slice_size],
                                     end_date=valid_dates[ed_idx + 2 * slice_size],
                                     interval="daily")

    res = list()
    for idx in range(st_idx, ed_idx):
        test_date = valid_dates[idx]
        criteria = three_plus_one_bin_slice(daily_data,
                                            test_date,
                                            slice_size=slice_size)
        if criteria:
            result = three_plus_one_return(daily_data,
                                           test_date,
                                           slice_size=slice_size)
            res.append(result)
    return res




# result = three_plus_one_bin_slice(conn, sec_symbol="TSLA", date_key_int=20210108, valid_dates=valid_dates, slice_size=10)
# print(result)
#
# result = three_plus_one_return(conn, sec_symbol="TSLA", date_key_int=20210108, valid_dates=valid_dates)

# res = validate_three_plus_one(conn, sec_symbol="CRNC",
#                               start_date_int=20200515,
#                               end_date_int=20210120,
#                               valid_dates=valid_dates,
#                               slice_size=15)
# df = pd.DataFrame(res)
# df.hist(bins=5)
# df.describe()


# res = validate_three_plus_one_op(conn, sec_symbol="CRNC",
#                                  start_date_int=20200515,
#                                  end_date_int=20210120,
#                                  valid_dates=valid_dates,
#                                  slice_size=15)
#
# df = pd.DataFrame(res)
# df.hist(bins=5)
# df.describe()





secs = read_sec_list('stock_security.csv')




all_results = list()
for each in secs:
    try:
        res = validate_three_plus_one_op(conn, sec_symbol=each,
                                         start_date_int=20200601,
                                         end_date_int=20210120,
                                         valid_dates=valid_dates,
                                         slice_size=15)
        df = pd.DataFrame(res)
        all_results.extend(res)
        print(f" mean = {df.mean().tolist()}, std = {df.std().tolist()}")
    except Exception as e:
        pass




df = pd.DataFrame(all_results)
df.hist(bins=100)
df.describe()