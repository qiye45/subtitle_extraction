# 导入必要的库
import cv2
from PIL import Image
import numpy as np
import os
import datetime
from rapidocr_onnxruntime import RapidOCR


# 定义函数,将秒数转换为时间格式
def format_time(second):
    hours = second // 3600
    minutes = (second - hours * 3600) // 60
    second = second - hours * 3600 - minutes * 60
    t = datetime.time(hour=hours, minute=minutes, second=second)
    return datetime.time.isoformat(t)


# 定义函数,计算两张图片的误差百分比
def cal_stderr(img, imgo=None):
    if imgo is None:
        return (img * 2).sum() / img.size * 100
    else:
        return ((img - imgo) * 2).sum() / img.size * 100


# 定义函数,将提取的字幕图片保存到指定文件夹
def save_image(ex_folder, img: Image, starts: int, ends: int):
    # 保存字幕图片到文件夹
    start_time = format_time(starts)
    end_time = format_time(ends)
    timeline = '-'.join([start_time, end_time]).replace(':','') + ".png"
    try:
        imgname = os.path.join(ex_folder, timeline)
        img.save(imgname)
        print('导出字幕图片 %s' % timeline)
    except Exception:
        print('导出字幕图片 %s 失败' % timeline)

ocr = RapidOCR(width_height_ratio=-1)

def img2text(file):
    resp = ""
    try:
        result, _ = ocr(file)
        if result:
            ocr_result = [line[1] for line in result]
            resp += "\n".join(ocr_result)
    except  Exception as e:
        print('img2text',e)
    return resp

# 定义主函数,导出视频中的字幕
def export_subtitle(video_filename):
    # 创建保存字幕图片的文件夹
    ex_folder = os.path.splitext(video_filename)[0]
    if not os.path.exists(ex_folder):
        os.mkdir(ex_folder)

    # 跳过开头帧数
    skip_frames = 2818

    # 打开视频文件
    videoCap = cv2.VideoCapture(video_filename)
    for i in range(skip_frames):
        videoCap.read()

    # 初始化参数
    start_frame = skip_frames
    curr_frame = skip_frames
    fps = videoCap.get(cv2.CAP_PROP_FPS)

    success = True
    subtitle_img = None
    last_img = None
    img_count = 0

    # 循环处理每一帧
    while success:

        # 跳过一些帧
        for j in range(9):
            videoCap.read()
            curr_frame += 1

        success, frame = videoCap.read()
        curr_frame += 1

        if frame is None:
            print('视频 %s 在第 %d 帧结束' % (video_filename, curr_frame))
            break

        # 预处理当前帧
        img = frame[:, :, 0]
        img = img[1000:1060, :]
        # img.show()
        # _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)

        # 如果变化太小,跳过
        if cal_stderr(img) < 1:
            continue

        # 处理第一张字幕图片
        if img_count == 0:
            subtitle_img = img
            print('视频 %s 在第 %d 帧导出字幕' % (video_filename, curr_frame))
            last_img = img
            img_count += 1
        # 如果字幕图片足够多了,保存结果
        elif img_count > 10:
            img_count = 0
            print('第 %s 帧' % curr_frame, img2text(subtitle_img))

            subtitle_img = Image.fromarray(subtitle_img)
            save_image(ex_folder, subtitle_img, int(start_frame / fps), int(curr_frame / fps))
            start_frame = curr_frame  # 开始时间往后移
        # 继续累积字幕图片
        else:
            if cal_stderr(img, last_img) > 1:
                subtitle_img = np.vstack((subtitle_img, img))
                last_img = img
                img_count += 1
            print('视频 %s 在第 %d 帧导出字幕' % (video_filename, curr_frame))

    # 保存最后的字幕结果
    if img_count > 0:
        subtitle_img = Image.fromarray(subtitle_img)
        save_image(ex_folder, subtitle_img, int(start_frame / fps), int(curr_frame / fps))

    print('视频 %s 字幕导出完成!' % video_filename)


if __name__ == '__main__':
    video_filename = '../test/video.mp4'
    export_subtitle(video_filename)
