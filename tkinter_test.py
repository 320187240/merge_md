import tkinter as tk
from tkinter import filedialog
import sys

print("尝试创建 Tk root...")
root = tk.Tk()
print("尝试隐藏 Tk root...")
root.withdraw()
print("尝试调用 askdirectory...")
try:
    # 添加一个 update 调用，有时有帮助
    root.update()
    folder = filedialog.askdirectory(title="测试选择文件夹")
    # 再次 update
    root.update()
    if folder:
        print(f"选择了文件夹: {folder}")
    else:
        print("取消了选择。")
except Exception as e:
    print(f"调用 askdirectory 时发生错误: {e}")
    import traceback
    traceback.print_exc() # 打印详细错误堆栈

print("测试脚本结束。")
# 可以尝试添加 root.destroy() 确保资源释放
# root.destroy() # 如果上面的代码执行不到这里，可以暂时注释掉
sys.exit() # 确保脚本退出