import asyncio
from bilibili_api import login_v2

async def main():
    qr = login_v2.QrCodeLogin()
    await qr.generate_qrcode()
    print('Please scan QR code for:', qr._QrCodeLogin__qr_link)
    
    for i in range(15):
        await asyncio.sleep(2)
        info = await qr.check_state()
        print(info)
        if qr.has_done():
            cred = qr.get_credential()
            print('bili_jct:', cred.bili_jct)
            print('dedeuserid:', cred.dedeuserid)
            print('sessdata:', cred.sessdata)
            print('buvid3:', cred.buvid3)
            break

asyncio.run(main())
