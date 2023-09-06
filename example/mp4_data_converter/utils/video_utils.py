import contextlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Tuple


def retrieve_video_metadata_from_video_file(video_file_path: Path) -> Dict[str, Any]:
    video_metadata = _get_video_metadata(video_file_path)
    video_meta = video_metadata.get("video", {})

    width, height = _extract_width_and_height(video_meta=video_meta)

    # Some codecs (i.e. MJPEG) may not carry aspect ratio information, so don't add it
    # aspect_ratio value of 0:1 is equal not n/a in ffprobe
    if "display_aspect_ratio" in video_meta and video_meta["display_aspect_ratio"] != "0:1":
        display_aspect_ratio = video_meta["display_aspect_ratio"]
    else:
        display_aspect_ratio = None

    return {
        "name": video_file_path.name,
        "width": width,
        "height": height,
        "bit_rate": int(video_metadata["format"]["bit_rate"]),
        "avg_frame_rate": video_meta["avg_frame_rate"],
        "codec_name": video_meta["codec_name"],
        "pix_fmt": video_meta["pix_fmt"],
        "duration": video_meta["duration"] if "duration" in video_meta else -1,
        "display_aspect_ratio": display_aspect_ratio,
        "audio_codec": video_metadata["audio"]["codec_name"]
        if video_metadata.get("audio", None) is not None
        else None,
    }


def _get_video_metadata(video_path: Path) -> Dict[str, Any]:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", str(video_path)]

    ffprobe_output_raw = subprocess.check_output(cmd).decode("utf-8")
    ffprobe_output = json.loads(ffprobe_output_raw)

    streams = ffprobe_output["streams"]

    meta_info = {stream["codec_type"].lower(): stream for stream in streams}
    meta_info["format"] = ffprobe_output["format"]

    return meta_info


def _extract_width_and_height(video_meta: Dict[str, Any]) -> Tuple[int, ...]:
    width = int(video_meta["width"])
    height = int(video_meta["height"])

    for side_data in video_meta.get("side_data_list", []):
        with contextlib.suppress(KeyError):
            if side_data["side_data_type"] != "Display Matrix":
                continue

            if side_data["rotation"] in [90, -90]:
                width, height = height, width
                break

    return width, height
