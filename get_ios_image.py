import os
import asyncio
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.afc import AfcService

# 将函数声明为异步函数 (async def)
async def backup_iphone_photos(local_export_path):
    if not os.path.exists(local_export_path):
        os.makedirs(local_export_path)

    try:
        # 1. 建立基础连接，必须使用 await 等待协程返回
        lockdown = await create_using_usbmux()
        print(f"成功连接设备。设备型号: {lockdown.product_type}")
        
        # 2. 启动 AFC 服务进行文件操作
        with AfcService(lockdown) as afc:
            remote_path = '/DCIM'
            
            print(f"正在从 iPhone 的 {remote_path} 目录递归下载文件...")
            # pull 方法负责拉取整个目录
            afc.pull(remote_path, local_export_path)
            
            print("文件复制已完成。")
            
    except Exception as e:
        print(f"发生错误: {e}")
        print("如果提示其他 coroutine 错误，说明该版本将 AfcService 也改为了异步。")

if __name__ == "__main__":
    save_path = r'C:\Users\1\Desktop\LocalSemanticSearch\手机相册'
    # 使用 asyncio.run() 启动事件循环并运行主协程
    asyncio.run(backup_iphone_photos(save_path))