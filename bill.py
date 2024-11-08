from paddleocr import PaddleOCR
import os
import csv
from natsort import natsorted

# 设置图片目录
img_dir = 'readable'
img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png'))]
img_files = natsorted(img_files)

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 创建统一的CSV文件
combined_csv = 'combined_results.csv'
all_data = []

for img_path in img_files:
    print(f"正在处理图片: {img_path}")
    try:
        # 修改图片路径，加入目录前缀
        full_img_path = os.path.join(img_dir, img_path)
        result = ocr.ocr(full_img_path, cls=True)
        
        # 用于存储核心信息的字典
        data = {
            "图片文件": img_path,
            "凭证编号": "",
            "日期": "",
            "收款人全称": "",
            "金额": "",
            "用途": ""
        }
        
        texts = [line[1][0] for line in result[0]]
        
        # 为20、21、22号文件创建详细的调试输出
        if img_path in ['20.png', '21.png', '22.png']:
            debug_filename = f'debug_output_{img_path.split(".")[0]}.txt'
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(f"=== OCR 完整结果 - {img_path} ===\n\n")
                for i, line in enumerate(result[0]):
                    text = line[1][0]  # 识别的文本
                    confidence = line[1][1]  # 置信度
                    box = line[0]  # 坐标框
                    f.write(f"序号 {i}:\n")
                    f.write(f"文本: {text}\n")
                    f.write(f"置信度: {confidence}\n")
                    f.write(f"位置: {box}\n")
                    f.write("-" * 50 + "\n")
        
        # 通过特征定位信息
        for i, text in enumerate(texts):
            # 凭证编号
            if text.startswith('第') and text.endswith('号'):
                data["凭证编号"] = f"'{text.replace('第', '').replace('号', '')}"
            
            # 日期
            if "年" in text and "日" in text:
                data["日期"] = text
            
            # 金额
            if any(text.startswith(symbol) for symbol in ['￥', '¥']):
                data["金额"] = text
            elif text == "金额（小写）":
                if i + 1 < len(texts):
                    next_text = texts[i + 1]
                    if any(symbol in next_text for symbol in ['￥', '¥']):
                        data["金额"] = next_text
            
            # 用途
            if text == "用途":
                if i + 1 < len(texts):
                    data["用途"] = texts[i + 1]

        # 收款人全称识别
        potential_names = []
        dates_index = -1
        account_index = -1
        service_station_count = 0
        
        # 首先找到日期和账号的位置，并统计服务站出现次数
        for i, text in enumerate(texts):
            if "年" in text and "日" in text:
                dates_index = i
            elif len(text) > 15 and text.replace(" ", "").isdigit():  # 长账号
                account_index = i
            if text == "桦川县水务综合服务站（零余额）":
                service_station_count += 1
        
        # 在日期和账号之间找到收款人全称
        if dates_index != -1 and account_index != -1:
            for i, text in enumerate(texts):
                if (dates_index < i < account_index and 
                    len(text) > 5 and 
                    not text.isdigit() and 
                    "银行" not in text):
                    # 特殊处理服务站
                    if text == "桦川县水务综合服务站（零余额）":
                        if service_station_count == 2:  # 只有出现两次时才认为是收款人
                            data["收款人全称"] = text
                            break
                    else:  # 其他情况直接认为是收款人
                        data["收款人全称"] = text
                        break

        all_data.append(data)
        print(f"已处理完成: {img_path}")

    except Exception as e:
        print(f"处理 {img_path} 时出错: {str(e)}")

# 将所有数据写入CSV文件
if all_data:
    with open(combined_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys(), quoting=csv.QUOTE_ALL)  # 添加 quoting 参数
        writer.writeheader()
        writer.writerows(all_data)
    print(f"\n所有数据已保存到: {combined_csv}")
else:
    print("没有成功处理任何图片")