import psutil
import math


def get_full_performance() -> dict:
    perf_dict = {
        'mem': None,
        'cpu': None
    }
    perf_dict_img = {
        0: '[🌑🌑🌑🌑🌑🌑🌑🌑🌑🌑]',
        5: '[🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑]',
        10: '[🌕🌑🌑🌑🌑🌑🌑🌑🌑🌑]',
        15: '[🌕🌗🌑🌑🌑🌑🌑🌑🌑🌑]',
        20: '[🌕🌕🌑🌑🌑🌑🌑🌑🌑🌑]',
        25: '[🌕🌕🌗🌑🌑🌑🌑🌑🌑🌑]',
        30: '[🌕🌕🌕🌑🌑🌑🌑🌑🌑🌑]',
        35: '[🌕🌕🌕🌗🌑🌑🌑🌑🌑🌑]',
        40: '[🌕🌕🌕🌕🌑🌑🌑🌑🌑🌑]',
        45: '[🌕🌕🌕🌕🌗🌑🌑🌑🌑🌑]',
        50: '[🌕🌕🌕🌕🌕🌑🌑🌑🌑🌑]',
        55: '[🌕🌕🌕🌕🌕🌗🌑🌑🌑🌑]',
        60: '[🌕🌕🌕🌕🌕🌕🌑🌑🌑🌑]',
        65: '[🌕🌕🌕🌕🌕🌕🌗🌑🌑🌑]',
        70: '[🌕🌕🌕🌕🌕🌕🌕🌑🌑🌑]',
        75: '[🌕🌕🌕🌕🌕🌕🌕🌗🌑🌑]',
        80: '[🌕🌕🌕🌕🌕🌕🌕🌕🌑🌑]',
        85: '[🌕🌕🌕🌕🌕🌕🌕🌕🌗🌑]',
        90: '[🌕🌕🌕🌕🌕🌕🌕🌕🌕🌑🌑]',
        95: '[🌕🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗]',
        100: '[🌕🌕🌕🌕🌕🌕🌕🌕🌕🌕]',
    }
    memory_full = psutil.virtual_memory()
    cpu_perc_load = psutil.cpu_percent(interval=1)
    memory_current_app = psutil.Process().memory_info().vms
    perf_dict['mem'] = f"Memory:\n" \
                       f"All - {round((memory_full.total/1024/1024)*0.001, 1)}GB\n" \
                       f"Usage - {round((memory_full.used/1024/1024)*0.001, 1)}GB\n" \
                       f"Free - {round((memory_full.free/1024/1024)*0.001, 1)}GB\n" \
                       f"This bot - {round(memory_current_app / 1024 / 1024, 2)}MB\n" \
                       f"{perf_dict_img[int(math.ceil(memory_full.percent/5.0)*5)]} {memory_full.percent}%\n"

    perf_dict['cpu'] = f"CPU:\n" \
                       f"{perf_dict_img[int(math.ceil(cpu_perc_load/5.0)*5)]} {cpu_perc_load}%\n"
    return perf_dict

