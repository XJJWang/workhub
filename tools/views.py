from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.contrib import messages
from paddleocr import PaddleOCR
import os
import csv
from natsort import natsorted
import tempfile
from django.http import FileResponse
import shutil

import logging
logger = logging.getLogger(__name__)


def bill_ocr(request):
    if request.method == 'POST':
        temp_dir = None
        try:
            # 检查是否有文件上传
            files = request.FILES.getlist('files[]')  # 修改参数名
            logger.info(f"接收到的请求方法: {request.method}")
            logger.info(f"接收到的文件数量: {len(files)}")
            logger.info(f"文件列表: {[f.name for f in files]}")
            logger.info(f"POST数据: {request.POST}")
            logger.info(f"FILES数据: {request.FILES}")
            
            if not files:
                logger.error("没有收到文件")
                return JsonResponse({
                    'status': 'error',
                    'message': '请选择要识别的图片文件'
                })

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            logger.info(f"创建临时目录: {temp_dir}")

            # 保存上传的图片
            saved_files = []
            for f in files:
                try:
                    file_path = os.path.join(temp_dir, f.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    saved_files.append(file_path)
                    logger.info(f"保存文件: {f.name}")
                except Exception as e:
                    logger.error(f"保存文件 {f.name} 失败: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'保存文件 {f.name} 失败: {str(e)}'
                    })

            # 初始化 PaddleOCR
            try:
                logger.info("初始化 PaddleOCR")
                ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            except Exception as e:
                logger.error(f"初始化 PaddleOCR 失败: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'初始化 OCR 引擎失败: {str(e)}'
                })

            # 处理图片
            all_data = []
            for file_path in saved_files:
                try:
                    logger.info(f"开始处理图片: {file_path}")
                    result = ocr.ocr(file_path, cls=True)
                    
                    if not result or not result[0]:
                        logger.warning(f"图片 {file_path} 未识别出内容")
                        continue

                    # 提取文本
                    texts = [line[1][0] for line in result[0]]
                    logger.info(f"识别出的文本数量: {len(texts)}")
                    logger.info(f"识别出的文本: {texts}")

                    # 初始化数据字典
                    data = {
                        "图片文件": os.path.basename(file_path),
                        "凭证编号": "",
                        "日期": "",
                        "收款人全称": "",
                        "金额": "",
                        "用途": ""
                    }

                    # 通过特征定位信息
                    for i, text in enumerate(texts):
                        # 凭证编号
                        if text.startswith('第') and text.endswith('号'):
                            data["凭证编号"] = f"'{text.replace('第', '').replace('号', '')}"
                            logger.info(f"找到凭证编号: {data['凭证编号']}")
                        
                        # 日期
                        if "年" in text and "日" in text:
                            data["日期"] = text
                            logger.info(f"找到日期: {data['日期']}")
                        
                        # 金额
                        if any(text.startswith(symbol) for symbol in ['￥', '¥']):
                            data["金额"] = text
                            logger.info(f"找到金额: {data['金额']}")
                        elif text == "金额（小写）":
                            if i + 1 < len(texts):
                                next_text = texts[i + 1]
                                if any(symbol in next_text for symbol in ['￥', '¥']):
                                    data["金额"] = next_text
                                    logger.info(f"找到金额（小写）: {data['金额']}")
                        
                        # 用途
                        if text == "用途":
                            if i + 1 < len(texts):
                                data["用途"] = texts[i + 1]
                                logger.info(f"找到用途: {data['用途']}")

                    # 收款人全称识别
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
                                        logger.info(f"找到收款人全称(服务站): {text}")
                                        break
                                else:  # 其他情况直接认为是收款人
                                    data["收款人全称"] = text
                                    logger.info(f"找到收款人全称: {text}")
                                    break

                    # 添加调试日志
                    logger.info(f"处理结果: {data}")
                    all_data.append(data)
                    logger.info(f"完成处理图片: {file_path}")

                except Exception as e:
                    logger.error(f"处理图片 {file_path} 时出错: {str(e)}")
                    continue  # 继续处理下一个文件，而不是立即返回

            # 检查处理结果
            logger.info(f"总共处理的文件数: {len(saved_files)}")
            logger.info(f"成功识别的文件数: {len(all_data)}")
            logger.info(f"识别结果: {all_data}")

            # 生成结果文件
            if all_data:
                try:
                    # 确保media目录存在
                    media_dir = os.path.join(settings.MEDIA_ROOT, 'ocr_results')
                    os.makedirs(media_dir, exist_ok=True)

                    # 创建结果文件
                    result_file = os.path.join(media_dir, 'results.csv')
                    with open(result_file, 'w', encoding='utf-8-sig', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                        writer.writeheader()
                        writer.writerows(all_data)

                    # 返回结果
                    result_url = f"{settings.MEDIA_URL}ocr_results/results.csv"
                    logger.info(f"生成结果文件: {result_url}")
                    
                    # 返回详细的处理结果
                    return JsonResponse({
                        'status': 'success',
                        'message': f'成功处理 {len(all_data)} 个文件',
                        'result_file': result_url,
                        'data': all_data,
                        'total_files': len(saved_files),
                        'processed_files': len(all_data)
                    })

                except Exception as e:
                    logger.error(f"生成结果文件失败: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'生成结果文件失败: {str(e)}'
                    })
            else:
                logger.warning("没有识别出有效数据")
                return JsonResponse({
                    'status': 'error',
                    'message': '没有识别出有效数据'
                })

        except Exception as e:
            logger.error(f"处理过程中出错: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'处理失败: {str(e)}'
            })

        finally:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("清理临时目录完成")
                except Exception as e:
                    logger.error(f"清理临时目录失败: {str(e)}")

    return render(request, 'tools/bill_ocr.html')