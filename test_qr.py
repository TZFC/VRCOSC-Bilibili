import asyncio
from bilibili_api import login_v2

async def main():
    login_info = await login_v2.get_qrcode()
    print('URL:', login_info.url)
    print('Token:', login_info.qrcode_key)

asyncio.run(main())
