import cv2
import ffmpeg
from mutagen.mp3 import MP3

import numpy as np

class Editor:

#region Image-to-Video
    @staticmethod
    def create_video_from_image(image_path: str, output_path: str, duration: float, video_style="zoom_in"):
        # Ensure style is valid
        accepted_styles = {"zoom_in", "breathing", "rotation"}
        if video_style not in accepted_styles:
            raise ValueError(f"The style: {video_style} is not a valid video style. Accepted Styles: {accepted_styles}")

        img = cv2.imread(image_path)


        match video_style:
            case "zoom_in":
                clip = Editor.apply_zoom_in_effect(img,output_path, duration)
            case "breathing":
                clip = Editor.apply_breathing_effect(img, duration)
            case "rotation":
                clip = Editor.apply_rotation_effect(img, duration)


    # @staticmethod
    # def apply_zoom_in_effect(clip, duration, zoom_factor=1.2):
    #     # Using a simple easing function for a smoother zoom
    #     return clip.zoom(t * zoom_factor / duration)

    @staticmethod
    def apply_zoom_in_effect(img, output_path, duration):
        height, width, _ = img.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        num_frames = int(duration * fps)
        scale_factor = 1.5

        for i in range(num_frames):
            scale = 1 + (scale_factor - 1) * (i / num_frames)
            M = cv2.getRotationMatrix2D((width / 2, height / 2), 0, scale)
            zoomed_img = cv2.warpAffine(img, M, (width, height))
            out.write(zoomed_img)

        out.release()


    @staticmethod
    def apply_zoom_out_effect(clip, duration):
        pass

    @staticmethod
    def apply_breathing_effect(clip, duration):
        pass

    @staticmethod
    def apply_rotation_effect(clip, duration):
        return clip.rotate(lambda t: 360 * t / duration, resample='bilinear')
#endregion


#region Audio
    @staticmethod
    def get_mp3_duration(file_path):
        audio = MP3(file_path)
        return audio.info.length

    @staticmethod
    def combine_audio_video(video_path, audio_path, output_path):
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path, y=None).run()


    @staticmethod
    def concatenate_videos(video_paths, output_path):
        inputs = [ffmpeg.input(video) for video in video_paths]
        video_streams = [input.video for input in inputs]
        audio_streams = [input.audio for input in inputs]

        # Concatenate video and audio separately
        concatenated_video = ffmpeg.concat(*video_streams, v=1, a=0)
        concatenated_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

        # Combine the concatenated video and audio streams
        ffmpeg.output(concatenated_video, concatenated_audio, output_path).run()

#endregion