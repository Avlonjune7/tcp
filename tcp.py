
python3 - <<'PY'
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

provinces = {
    "北京": "bj", "天津": "tj", "上海": "sh", "重庆": "cq",
    "河北": "he", "山西": "sx", "辽宁": "ln", "吉林": "jl",
    "黑龙江": "hl", "江苏": "js", "浙江": "zj", "安徽": "ah",
    "福建": "fj", "江西": "jx", "山东": "sd", "河南": "ha",
    "湖北": "hb", "湖南": "hn", "广东": "gd", "海南": "hi",
    "四川": "sc", "贵州": "gz", "云南": "yn", "陕西": "sn",
    "甘肃": "gs", "青海": "qh", "内蒙古": "nm", "广西": "gx",
    "西藏": "xz", "宁夏": "nx", "新疆": "xj"
}

carriers = {"电信": "ct", "联通": "cu", "移动": "cm"}

def test(province, code, carrier, ccode):
    host = f"{code}-{ccode}-v4.ip.zstaticcdn.com"
    start = time.monotonic()
    try:
        with socket.create_connection((host, 80), timeout=3):
            ms = (time.monotonic() - start) * 1000
            return province, carrier, True, f"{ms:.0f}ms"
    except OSError:
        return province, carrier, False, "失败"

print("开始检测全国31省三网TCP 80端口...")
print("-" * 65)

results = {}
tasks = []

with ThreadPoolExecutor(max_workers=15) as pool:
    for province, code in provinces.items():
        for carrier, ccode in carriers.items():
            tasks.append(pool.submit(
                test, province, code, carrier, ccode
            ))

    for future in as_completed(tasks):
        p, c, ok, delay = future.result()
        results[(p, c)] = (ok, delay)

stats = {c: [0, 0] for c in carriers}

for province in provinces:
    line = f"{province:<4} "
    for carrier in carriers:
        ok, delay = results[(province, carrier)]
        stats[carrier][1] += 1
        if ok:
            stats[carrier][0] += 1
        line += f" {carrier}:{'✅' if ok else '❌'}{delay:<8}"
    print(line)

print("-" * 65)
total_ok = sum(v[0] for v in stats.values())
total = sum(v[1] for v in stats.values())

for carrier, (ok, n) in stats.items():
    print(f"{carrier}：{ok}/{n} 成功 ({ok/n*100:.1f}%)")

print(f"总计：{total_ok}/{total} 成功 ({total_ok/total*100:.1f}%)")
PY
