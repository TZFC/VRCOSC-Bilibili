import browser_cookie3
import traceback

print('Testing Chrome...')
try:
    cj = browser_cookie3.chrome(domain_name='.bilibili.com')
    print('Chrome cookies:', len(cj))
    for c in cj:
        if c.name in ('bili_jct', 'DedeUserID', 'SESSDATA'):
            print(c.name, c.value[:5])
except Exception as e:
    traceback.print_exc()

print('Testing Edge...')
try:
    cj = browser_cookie3.edge(domain_name='.bilibili.com')
    print('Edge cookies:', len(cj))
    for c in cj:
        if c.name in ('bili_jct', 'DedeUserID', 'SESSDATA'):
            print(c.name, c.value[:5])
except Exception as e:
    traceback.print_exc()
