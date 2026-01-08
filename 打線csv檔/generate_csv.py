#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 CSV 文件的腳本
從每個資料夾的 main.txt 讀取數據，生成對應的 CSV 文件
"""

import os
import csv
from pathlib import Path
from collections import defaultdict


def parse_main_txt(file_path):
    """
    解析 main.txt 文件，返回區塊一和區塊二的數據
    返回: (block1_dict, block2_dict) 其中 dict 的 key 是長度，value 是數量
    """
    block1 = defaultdict(int)  # 長度 -> 數量
    block2 = defaultdict(int)  # 長度 -> 數量
    
    current_block = 1
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 空行表示區塊分隔
            if not line:
                if current_block == 1:
                    current_block = 2
                continue
            
            # 解析 長度\t數量
            parts = line.split('\t')
            if len(parts) == 2:
                try:
                    length = int(parts[0].strip())
                    quantity = int(parts[1].strip())
                    if current_block == 1:
                        block1[length] += quantity
                    else:
                        block2[length] += quantity
                except ValueError:
                    continue
    
    return dict(block1), dict(block2)


def merge_data(data_list):
    """
    合併多個數據字典，將相同長度的數量相加
    """
    merged = defaultdict(int)
    for data in data_list:
        for length, quantity in data.items():
            merged[length] += quantity
    return dict(merged)


def write_csv(file_path, data_dict):
    """
    將數據寫入 CSV 文件，格式：長度,數量
    按長度排序，過濾掉數量為0的數據
    """
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 寫入標題行（可選，如果需要可以取消註釋）
        # writer.writerow(['長度', '數量'])
        
        # 按長度排序後寫入，過濾掉數量為0的數據
        for length in sorted(data_dict.keys()):
            quantity = data_dict[length]
            if quantity != 0:  # 只寫入數量不為0的數據
                writer.writerow([length, quantity])


def process_folder(folder_path):
    """
    處理單個資料夾，生成對應的 CSV 文件
    """
    main_txt = os.path.join(folder_path, 'main.txt')
    
    if not os.path.exists(main_txt):
        print(f"警告: {folder_path} 中沒有找到 main.txt，跳過")
        return
    
    print(f"處理資料夾: {folder_path}")
    
    # 解析 main.txt
    block1, block2 = parse_main_txt(main_txt)
    
    # 生成各 CSV 文件
    # red.csv 和 black.csv: 所有區塊的數據合併
    all_blocks = merge_data([block1, block2])
    write_csv(os.path.join(folder_path, 'red.csv'), all_blocks)
    write_csv(os.path.join(folder_path, 'black.csv'), all_blocks)
    
    # green.csv 和 blue.csv: 第一個區塊
    write_csv(os.path.join(folder_path, 'green.csv'), block1)
    write_csv(os.path.join(folder_path, 'blue.csv'), block1)
    
    # yellow.csv: 第二個區塊
    write_csv(os.path.join(folder_path, 'yellow.csv'), block2)
    
    print(f"  ✓ 已生成: red.csv, black.csv, green.csv, blue.csv, yellow.csv")


def main():
    """
    主函數：找到所有包含 main.txt 的資料夾並處理
    """
    # 獲取腳本所在目錄
    script_dir = Path(__file__).parent
    
    # 找到所有包含 main.txt 的資料夾
    folders = []
    for item in script_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            main_txt = item / 'main.txt'
            if main_txt.exists():
                folders.append(str(item))
    
    if not folders:
        print("沒有找到包含 main.txt 的資料夾")
        return
    
    # 按名稱排序
    folders.sort()
    
    print(f"找到 {len(folders)} 個資料夾需要處理\n")
    
    # 處理每個資料夾
    for folder in folders:
        process_folder(folder)
        print()
    
    print("所有處理完成！")


if __name__ == '__main__':
    main()

