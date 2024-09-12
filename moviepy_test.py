from moviepy.editor import *

img1  =  ImageClip("test_assets/1.webp")
img2  =  ImageClip("test_assets/2.jpg")
img3  =  ImageClip("test_assets/3.webp")
img4  =  ImageClip("https://ideogram.ai/api/images/direct/8YEpFzHuS-S6xXEGmCsf7g")

img1 = img1.set_duration(5)
img2 = img2.set_duration(5)
img3 = img3.set_duration(5)
img4 = img4.set_duration(5)

custom_padding = 1

final_video = concatenate(
    [
        img1,
        img2.crossfadein(custom_padding),
        img3.crossfadein(custom_padding),
        img4.crossfadein(custom_padding)
    ],
    padding=0,
    method="compose"
)


final_video.write_videofile("test_assets/1_test.mp4", codec="libx264", fps=24)