
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROVINCES = {
    "北京": "bj", "天津": "tj", "上海": "sh", "重庆": "cq",
    "河北": "he", "山西": "sx", "辽宁": "ln", "吉林": "jl",
    "黑龙江": "hl", "江苏": "js", "浙江": "zj", "安徽": "ah",
    "福建": "fj", "江西": "jx", "山东": "sd", "河南": "ha",
    "湖北": "hb", "湖南": "hn", "广东": "gd", "海南": "hi",
    "四川": "sc", "贵州": "gz", "云南": "yn", "陕西": "sn",
    "甘肃": "gs", "青海": "qh", "内蒙古": "nm", "广西": "gx",
    "西藏": "xz", "宁夏": "nx", "新疆": "xj"
}

CARRIERS = {"电信": "ct", "联通": "cu", "移动": "cm"}

PORT = 80
TIMEOUT = 2
WORKERS = 64


def check(province, code, carrier, carrier_code):
    host = f"{code}-{carrier_code}-v4.ip.zstaticcdn.com"

    try:
        # DNS 查询独立于 TCP 计时
        addresses = socket.getaddrinfo(
            host, PORT, socket.AF_INET, socket.SOCK_STREAM
        )
        ip = addresses[0][4][0]
    except socket.gaierror:
        return province, carrier, False, "DNS错误"

    start = time.perf_counter()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((ip, PORT))

        ms = (time.perf_counter() - start) * 1000
        return province, carrier, True, f"{ms:.0f}ms"

    except socket.timeout:
        return province, carrier, False, "超时"
    except ConnectionRefusedError:
        return province, carrier, False, "拒绝"
    except OSError:
        return province, carrier, False, "网络错误"


def main():
    start = time.perf_counter()
    print(f"🇨🇳 全国31省三网TCP检测 | {WORKERS}并发 | 超时{TIMEOUT}s")
    print("-" * 72)

    results = {}
    stats = {c: 0 for c in CARRIERS}

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        tasks = [
            pool.submit(check, p, code, c, cc)
            for p, code in PROVINCES.items()
            for c, cc in CARRIERS.items()
        ]

        for future in as_completed(tasks):
            p, c, ok, delay = future.result()
            results[(p, c)] = (ok, delay)

    for province in PROVINCES:
        parts = [f"{province:<4}"]
        for carrier in CARRIERS:
            ok, delay = results[(province, carrier)]
            if ok:
                stats[carrier] += 1
            parts.append(
                f"{carrier}:{'✅' if ok else '❌'}{delay:<9}"
            )
        print(" ".join(parts))

    print("-" * 72)

    total_ok = sum(stats.values())
    total = len(PROVINCES) * len(CARRIERS)

    for carrier, count in stats.items():
        print(f"{carrier}：{count}/31 ({count/31*100:.1f}%)")

    print(f"总计：{total_ok}/{total} ({total_ok/total*100:.1f}%)")
    print(f"总耗时：{time.perf_counter()-start:.2f}秒")


if __name__ == "__main__":
    main()
