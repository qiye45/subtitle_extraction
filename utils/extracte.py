import cv2
from PIL import Image
import numpy as np
import os
import datetime


def format_time(second):
    hours = second // 3600
    minutes = (second - hours * 3600) // 60
    second = second - hours * 3600 - minutes * 60
    t = datetime.time(hour=hours, minute=minutes, second=second)
    return datetime.time.isoformat(t)


def cal_stderr(img, imgo=None):
    if imgo is None:
        return (img ** 2).sum() / img.size * 100
    else:
        return ((img - imgo) ** 2).sum() / img.size * 100


def save_image(ex_folder, img: Image, starts: int, ends: int):
    # 保存字幕图片到文件夹
    start_time = format_time(starts)
    end_time = format_time(ends)
    timeline = '-'.join([start_time, end_time]) + ".png"
    try:
        imgname = os.path.join(ex_folder, timeline)
        img.save(imgname)
        print('export subtitle at %s' % timeline)
    except Exception:
        print('export subtitle at %s error' % timeline)


def export_subtitle(video_filename):
    ex_folder = os.path.splitext(video_filename)[0]
    if not os.path.exists(ex_folder):
        os.mkdir(ex_folder)
    skip_frames = 2818
    videoCap = cv2.VideoCapture(video_filename)
    for i in range(skip_frames):
        videoCap.read()
    start_frame = skip_frames
    curr_frame = skip_frames
    fps = videoCap.get(cv2.CAP_PROP_FPS)
    success = True
    subtitle_img = None
    last_img = None
    img_count = 0
    while success:
        for j in range(9):
            videoCap.read()
            curr_frame += 1
        success, frame = videoCap.read()
        curr_frame += 1
        if frame is None:
            print('video: %s finish at %d frame.' % (video_filename, curr_frame))
            break

        img = frame[:, :, 0]
        img = img[495:570, :]
        _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)

        if cal_stderr(img) < 1:
            continue

        if img_count == 0:
            subtitle_img = img
            print('video: %s add subtitle at %d frame.' % (video_filename, curr_frame))
            last_img = img
            img_count += 1
        elif img_count > 10:
            img_count = 0
            subtitle_img = Image.fromarray(subtitle_img)
            save_image(ex_folder, subtitle_img, int(start_frame/fps), int(curr_frame/fps))
            start_frame = curr_frame    # 开始时间往后移
        else:
            if cal_stderr(img, last_img) > 1:
                subtitle_img = np.vstack((subtitle_img, img))
                last_img = img
                img_count += 1
                print('video: %s add subtitle at %d frame.' % (video_filename, curr_frame))
    if img_count > 0:
        subtitle_img = Image.fromarray(subtitle_img)
        save_image(ex_folder, subtitle_img, int(start_frame / fps), int(curr_frame / fps))
    print('video: %s export subtitle finish!' % video_filename)


if __name__ == '__main__':
    video_filename = '/Users/csd/S01E01.mkv'
    export_subtitle(video_filename)