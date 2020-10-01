import os
import re
import io
import sys
import shutil
import imageio
import argparse
from pathlib import Path
from pytube import YouTube
from PIL import Image, ImageDraw, ImageSequence, ImageFont


class TargetFormat(object):
    GIF = ".gif"
    MP4 = ".mp4"
    AVI = ".avi"


def arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='GIF maker from YouTube Video')
    parser.add_argument('--url', help='YouTube Link.')
    parser.add_argument('--dir', help='Local Output Directory.')
    parser.add_argument('--start', help='Starting time point.')
    parser.add_argument('--end', help='Ending time point.')
    parser.add_argument('--text', help='GIF Text.')
    args = parser.parse_args()
    return args


def convertFile(inputpath, targetFormat):
    outputpath = os.path.splitext(inputpath)[0] + targetFormat
    reader = imageio.get_reader(inputpath)
    fps = reader.get_meta_data()['fps']
    writer = imageio.get_writer(outputpath, fps=fps)
    for i,im in enumerate(reader):
        sys.stdout.write("\rframe {0}".format(i))
        sys.stdout.flush()
        writer.append_data(im)
    writer.close()


def youtube_downloader(url, local_dir):
    yt = YouTube(url)
    ys = yt.streams.get_highest_resolution()
    ys.download(local_dir)
    filepath = local_dir + '\\' + yt.title + '.mp4'
    return filepath, yt.title


def cmd(command):
	os.system(command)


def crop(start, end, input, output):
	command = "ffmpeg -i " + input + " -ss  " + start + " -to " + end + " -c copy " + output
	cmd(command)


def add_Text2Gif(gif_file, gif_text, out_gif_path):
    im = Image.open(gif_file)
    # A list of the frames to be outputted
    frames = []
    # Loop over each frame in the animated image
    w, h = im.size
    for frame in ImageSequence.Iterator(im):
        # Draw the text on the frame
        d = ImageDraw.Draw(frame)
        font = ImageFont.truetype(font="arial.ttf", size=40, index=0, encoding='unic')
        text_w, text_h = d.textsize(gif_text, font)
        d.text(((w - text_w) // 2, h - text_h - h * 0.01), gif_text, font=font)
        del d
        b = io.BytesIO()
        frame.save(b, format="GIF")
        frame = Image.open(b)
        frames.append(frame)
    # Save the frames as a new image
    frames[0].save(out_gif_path, save_all=True, append_images=frames[1:])


def main():
    options = arguments(sys.argv[1:])
    Path(options.dir).mkdir(parents=True, exist_ok=True)
    filepath, title = youtube_downloader(options.url, options.dir)
    os.rename(filepath, options.dir + '\\tmp.mp4')
    crop(options.start, options.end, options.dir + '\\tmp.mp4', options.dir + '\\cropped.mp4')
    convertFile(options.dir + '\\cropped.mp4', TargetFormat.GIF)
    os.remove(options.dir + '\\cropped.mp4')
    os.remove(options.dir + '\\tmp.mp4')
    add_Text2Gif(options.dir + '\\cropped.gif', options.text ,  options.dir + '\\' + title + '.gif')
    os.remove(options.dir + '\\cropped.gif')


if __name__ == '__main__':
    main()
