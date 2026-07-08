with open("bot_code/analyzer/fetcher.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'q = r.json()["chart"]["result"][0]["indicators"]["quote"][0]' in line:
        lines[i] = '''                j = r.json()
                if not j.get("chart", {}).get("result"):
                    continue
                q = j["chart"]["result"][0]["indicators"]["quote"][0]
'''
        break

with open("bot_code/analyzer/fetcher.py", "w") as f:
    f.writelines(lines)
print("Patched fetcher.py")
