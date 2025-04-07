# -*- coding: utf-8 -*-
import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import datetime
import re
import traceback

def sanitize_filename(name):
    """清理字符串，使其适合作为文件名的一部分"""
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name

def merge_markdown_files(input_dir, output_file):
    """
    合并指定目录及其子目录下的所有 Markdown (.md) 文件到单个输出文件中,
    并使用 Markdown 标题表示目录结构。

    Args:
        input_dir (str): 要搜索 .md 文件的目录路径。
        output_file (str): 合并后内容的输出文件路径。
    """
    # print(f"DEBUG: 进入 merge_markdown_files 函数。输入='{input_dir}', 输出='{output_file}'")

    # --- 省略路径检查，主程序已做 ---

    output_lines = []  # 用于存储最终输出的 Markdown 文本行
    file_count = 0
    processed_dirs = set() # 记录已添加标题的目录，避免重复

    # 添加一个顶层标题，指明来源
    input_folder_name = os.path.basename(input_dir)
    output_lines.append(f"# 合并内容来源: {input_folder_name}\n")
    # print(f"DEBUG: 添加顶层标题: 合并内容来源: {input_folder_name}")

    # print(f"开始合并过程，源目录: '{input_dir}'")
    # print(f"输出将保存到: '{output_file}'")
    # print("DEBUG: 准备开始遍历目录并构建结构化内容...")

    # --- 遍历目录并生成结构化 Markdown ---
    try:
        # 保证处理顺序，先排序获取所有路径
        all_paths = []
        for root, dirs, files in os.walk(input_dir, topdown=True):
            # 标准化路径以进行可靠排序和处理
            root_norm = os.path.normpath(root)
            dirs_norm = sorted([os.path.normpath(os.path.join(root, d)) for d in dirs])
            files_norm = sorted([os.path.normpath(os.path.join(root, f)) for f in files if f.lower().endswith('.md')])
            all_paths.append((root_norm, dirs_norm, files_norm))

        # 按根路径排序，确保父目录先于子目录处理
        all_paths.sort(key=lambda x: x[0])

        for root, dirs, files in all_paths: # 使用排序后的路径
            # --- 计算当前目录深度和相对路径 ---
            relative_path_dir = os.path.relpath(root, input_dir)
            depth = 0
            if relative_path_dir != '.':
                # depth = relative_path_dir.count(os.sep) # 不可靠
                depth = len(relative_path_dir.split(os.sep))
            # print(f"DEBUG: 处理目录: '{relative_path_dir}' (标准化: '{root}'), 深度: {depth}")

            # --- 添加目录标题 (如果需要且未添加过) ---
            # 调整：只在处理该目录下的第一个文件时添加上级目录标题，避免空目录标题
            current_dir_title_added = False

            # --- 处理当前目录下的 Markdown 文件 ---
            for file_path in files: # files 已经是排序过的完整路径
                filename = os.path.basename(file_path)
                relative_path_file = os.path.relpath(file_path, input_dir)

                # --- 如果当前目录标题还没添加，现在添加 ---
                # 只有当该目录下确实有 .md 文件时才添加目录标题
                if depth > 0 and root not in processed_dirs:
                     dir_heading_level = '#' * (depth + 1) # 目录标题级别 = 深度 + 1 (##, ###, ...)
                     output_lines.append(f"\n{dir_heading_level} 目录: {os.path.basename(root)}\n")
                     # print(f"  DEBUG: 添加目录标题: {dir_heading_level} 目录: {os.path.basename(root)}")
                     processed_dirs.add(root) # 标记为已处理
                     current_dir_title_added = True # 标记本轮已添加

                # print(f"  正在处理文件: {relative_path_file}")

                # --- 添加文件标题 ---
                # 文件标题级别比其所在目录低一级（即深度+2）
                file_heading_level = '#' * (depth + 2)
                # 如果目录标题刚被添加，文件标题前加少一个换行符
                newline_before_file = "\n" if not current_dir_title_added else ""
                output_lines.append(f"{newline_before_file}{file_heading_level} 文件: {filename}\n")
                # print(f"    DEBUG: 添加文件标题: {file_heading_level} 文件: {filename}")
                current_dir_title_added = False # 重置标记

                # --- 读取并添加文件内容 ---
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        # 添加原始路径作为注释（可选）
                        # output_lines.append(f"<!-- 原始路径: {relative_path_file} -->\n")
                        output_lines.append(content)
                        output_lines.append("\n") # 在文件内容后加一个换行符，与下一个标题分隔
                        file_count += 1
                        # print(f"      -> 已添加 {len(content)} 字符内容")

                except FileNotFoundError:
                    output_lines.append(f"*警告: 文件在读取前消失: {relative_path_file}*\n")
                    # print(f"  警告: 文件在读取前消失: {file_path}")
                except Exception as e:
                    error_msg = f"*错误: 读取文件 {relative_path_file} 时出错: {e}*\n"
                    output_lines.append(error_msg)
                    # print(f"  读取文件 {file_path} 时出错: {e}")
                    # 不弹窗中断，继续处理其他文件

    except Exception as e:
        error_msg_walk = f"\n\n*严重错误: 遍历目录或构建内容时出错: {e}*\n"
        output_lines.append(error_msg_walk)
        # print(f"错误: 遍历目录或构建内容时出错: {e}")
        traceback.print_exc()
        # 即使遍历出错，也尝试写入已收集的内容
        # messagebox.showerror("遍历错误", f"遍历目录 '{input_dir}' 时发生错误: {e}")
        # return # 不在此处返回，继续尝试写入

    # print(f"DEBUG: 内容构建完成。共处理 {file_count} 个 .md 文件。准备写入输出文件。")
    # print(f"DEBUG: output_lines 列表包含 {len(output_lines)} 行。")

    # --- 写入文件 ---
    output_file_norm = os.path.normpath(output_file)
    write_successful = False
    final_content = "".join(output_lines) # 使用 "" 连接，因为行尾已包含 \n
    # print(f"DEBUG: 最终待写入字符串总长度: {len(final_content)}")

    try:
        with open(output_file_norm, 'w', encoding='utf-8') as outfile:
            # print(f"DEBUG: 文件 '{output_file_norm}' 已成功打开用于写入。")
            bytes_written = outfile.write(final_content)
            # print(f"DEBUG: outfile.write() 调用完成，报告写入 {bytes_written} 个字符。")
            # print(f"DEBUG: 尝试强制刷新缓冲区 (outfile.flush())...")
            outfile.flush()
            # print(f"DEBUG: outfile.flush() 调用完成。")
            # 在 with 块内部检查文件大小
            try:
                outfile.seek(0, os.SEEK_END)
                size_inside_with = outfile.tell()
                # print(f"DEBUG: 在 with 块内部，刷新后，文件指针位置 (大小): {size_inside_with}")
            except Exception as size_err:
                messagebox.showinfo("检查失败", "检查文件大小时出错。")
                # print(f"DEBUG: 在 with 块内部检查文件大小时出错: {size_err}")

        # print(f"DEBUG: with open(...) 块已退出，文件应已关闭和刷新。")
        write_successful = True

    except Exception as e:
        messagebox.showerror("写入错误", f"写入合并文件时发生严重错误:\n{output_file_norm}\n错误: {e}")
        traceback.print_exc()

    # --- 写入后验证 ---
    # if write_successful:
    #     print("DEBUG: 尝试在写入操作后检查文件状态...")
    #     try:
    #         if os.path.exists(output_file_norm):
    #             file_size = os.path.getsize(output_file_norm)
    #             print(f"DEBUG: 文件 '{output_file_norm}' 存在，大小为: {file_size} 字节。")
    #             if file_size > 0 or file_count == 0: # 允许0字节如果确实没找到文件
    #                 success_msg = f"成功合并 {file_count} 个 Markdown 文件到:\n'{output_file_norm}'"
    #                 if file_count > 0 :
    #                      success_msg += f"\n文件大小: {file_size} 字节"
    #                 print(f"\n{success_msg.replace('\\n', ' ')}") # 打印单行日志
    #                 messagebox.showinfo("合并完成", success_msg)
    #             else:
    #                 print(f"错误: 文件 '{output_file_norm}' 已创建但大小为 0 字节！写入操作可能未完全成功。")
    #                 messagebox.showerror("写入问题", f"文件已创建但大小为 0:\n'{output_file_norm}'\n请检查日志和磁盘空间/权限。")
    #         else:
    #             print(f"错误: 文件 '{output_file_norm}' 在写入后未找到！")
    #             messagebox.showerror("写入失败", f"写入操作后未能找到文件:\n'{output_file_norm}'")
    #     except Exception as post_check_err:
    #         print(f"DEBUG: 写入后检查文件状态时出错: {post_check_err}")
    #         messagebox.showwarning("合并完成（检查出错）", f"合并过程可能已完成，但在检查最终文件时出错。\n请手动检查文件:\n'{output_file_norm}'")
    # else:
    #     print("写入过程因错误未能成功完成。")


# --- 主程序入口  ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    # 1. 选择源文件夹
    input_directory = filedialog.askdirectory(title="请选择【包含 .md 文件】的源文件夹")
    input_directory = os.path.normpath(input_directory) if input_directory else None
    if not input_directory:
        messagebox.showinfo("操作取消", "未选择源文件夹，操作已取消。")
        sys.exit(0)
    if not os.path.isdir(input_directory):
         messagebox.showerror("路径无效", f"选择的源路径不是有效目录:\n'{input_directory}'")
         sys.exit(1)

    # 2. 选择输出文件夹
    output_directory = filedialog.askdirectory(title="请选择【保存合并文件】的目标文件夹")
    output_directory = os.path.normpath(output_directory) if output_directory else None
    if not output_directory:
        messagebox.showinfo("操作取消", "未选择输出文件夹，操作已取消。")
        sys.exit(0)
    if not os.path.isdir(output_directory):
         messagebox.showerror("路径无效", f"选择的输出文件夹不是有效目录:\n'{output_directory}'")
         sys.exit(1)

    # 3. 生成输出文件名
    try:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        input_folder_name = os.path.basename(input_directory)
        sanitized_folder_name = sanitize_filename(input_folder_name)
        output_filename = f"{sanitized_folder_name}_结构化合并_{current_date}.md" # 文件名加了“结构化”
        output_filepath = os.path.normpath(os.path.join(output_directory, output_filename))

    except Exception as e:
        messagebox.showerror("错误", f"生成输出文件名或路径时出错:\n{e}")
        traceback.print_exc()
        sys.exit(1)

    # 4. 调用合并函数
    if os.path.isdir(output_directory):
        merge_markdown_files(input_directory, output_filepath)
    else:
        messagebox.showerror("内部错误", f"输出文件夹 '{output_directory}' 在调用合并前检查无效。")
