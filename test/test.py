import cv2
from rapidocr_onnxruntime import RapidOCR

video_filename = 'video.mp4'
videoCap = cv2.VideoCapture(video_filename)

# 帧频
fps = videoCap.get(cv2.CAP_PROP_FPS)
# 视频总帧数
total_frames = int(videoCap.get(cv2.CAP_PROP_FRAME_COUNT))
# 图像尺寸
image_size = (int(videoCap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(videoCap.get(cv2.CAP_PROP_FRAME_WIDTH)))

print(fps)
print(total_frames)
print(image_size)

for i in range(10):
    sucess, frame = videoCap.read()

from PIL import Image

img = Image.fromarray(frame)
# img.show()

im0 = frame[:, :, 0]
im = im0[1000:1060, :]     #  确定字幕的范围，注意不同的视频文件剪切的索引值不同
img = Image.fromarray(im0)
img.show()

ocr = RapidOCR()

def img2text(filepath):
    resp = ""
    result, _ = ocr(filepath)
    if result:
        ocr_result = [line[1] for line in result]
        resp += "\n".join(ocr_result)
    return resp

print(img2text(im0))