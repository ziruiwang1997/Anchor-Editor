"""
views.py: Views for ReadAlong Studio web application

Interactions are described as websocket events and responses
Corresponding JavaScript is found in readalongs/static/js/main.js
"""

import io
import os
import re
from datetime import datetime
from pathlib import Path
from subprocess import run
from tempfile import mkdtemp
from zipfile import ZipFile

from flask import abort, redirect, render_template, request, send_file, session, url_for
from flask_socketio import emit

from readalongs.app import app, socketio
from readalongs.log import LOGGER
from readalongs.util import get_langs

ALLOWED_TEXT = ["txt", "xml", "docx"]
ALLOWED_AUDIO = ["wav", "mp3"]
ALLOWED_G2P = ["csv", "xlsx"]
ALLOWED_EXTENSIONS = set(ALLOWED_AUDIO + ALLOWED_G2P + ALLOWED_TEXT)


def allowed_file(filename: str) -> bool:
    """Determines whether filename is allowable

    Args:
        filename (str): a filename

    Returns:
        bool: True if allowed
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_decode(byte_seq: bytes) -> str:
    """Convert byte_seq to str if it's valid utf8, otherwise return its str rep

    Does not raise any exceptions: non-utf8 inputs will yield escaped specials.
    """
    try:
        return byte_seq.decode()
    except UnicodeDecodeError:
        return str(byte_seq)


def uploaded_files(dir_path: str) -> dict:
    """Returns all files that have been uploaded

    Args:
        dir_path (str): path to directory where uploaded files are

    Returns:
        dict: A dictionary containing three keys:
               - audio : A list containing all paths to audio files
               - text  : A list containing all paths to text files
               - maps  : A list containing all paths to mapping files
    """
    upload_dir = Path(dir_path)
    audio = list(upload_dir.glob("*.wav")) + list(upload_dir.glob("*.mp3"))
    text = (
        list(upload_dir.glob("*.txt"))
        + list(upload_dir.glob("*.xml"))
        + list(upload_dir.glob("*.docx"))
    )
    maps = list(upload_dir.glob("*.csv")) + list(upload_dir.glob("*.xlsx"))
    return {
        "audio": [{"path": str(x), "fn": os.path.basename(str(x))} for x in audio],
        "text": [{"path": str(x), "fn": os.path.basename(str(x))} for x in text],
        "maps": [{"path": str(x), "fn": os.path.basename(str(x))} for x in maps],
    }


def update_session_config(**kwargs) -> dict:
    """Update the session configuration for running readalongs aligner.

    Args:
        **kwargs: Arbitrary keyword arguments, which will update the session config

    Returns:
        dict: Returns the updated session configuration
    """
    previous_config = session.get("config", {})
    session["config"] = {**previous_config, **kwargs}
    return session["config"]


@app.route("/")
def home():
    """ Home View - go to Step 1 which is for uploading files """
    return redirect(url_for("steps", step=1))


@socketio.on("config update event", namespace="/config")
def update_config(message):
    emit("config update response", {"data": update_session_config(**message)})


@socketio.on("upload event", namespace="/file")
def upload(message):
    if message["type"] == "audio":
        save_path = os.path.join(session["temp_dir"], message["name"])
        session["audio"] = save_path
    if message["type"] == "text":
        save_path = os.path.join(session["temp_dir"], message["name"])
        session["text"] = save_path
    if message["type"] == "mapping":
        save_path = os.path.join(session["temp_dir"], message["name"])
        if "config" in session and "lang" in session["config"]["lang"]:
            del session["config"]["lang"]
        session["mapping"] = save_path
    with open(save_path, "wb") as f:
        f.write(message["data"]["file"])
    emit("upload response", {"data": {"path": save_path}})


# @SOCKETIO.on('remove event', namespace='/file')
# def remove_f(message):
#     path_to_remove = message['data']['path_to_remove']
#     if os.path.exists(path_to_remove) and os.path.isfile(path_to_remove):
#         os.remove(path_to_remove)
#     emit('remove response', {'data': {'removed_file': os.path.basename(path_to_remove)}})

# @SOCKETIO.on('upload event' namespace='file')
# def upload_f(message):


@app.route("/remove", methods=["POST"])
def remove_file():
    if request.method == "POST":
        path = request.data.decode("utf8").split("=")[1]
        os.remove(path)
    return redirect(url_for("steps", step=1))


@app.route("/step/<int:step>")
def steps(step):
    """ Go through steps """
    if step == 1:
        session.clear()
        session["temp_dir"] = mkdtemp()
        temp_dir = session["temp_dir"]
        langs, lang_names = get_langs()
        return render_template(
            "upload.html",
            uploaded=uploaded_files(temp_dir),
            maps=[{"code": m, "name": lang_names[m]} for m in langs],
        )
    elif step == 2:
        return render_template("preview.html")
    elif step == 3:
        if "audio" not in session or "text" not in session:
            log = "Sorry, it looks like something is wrong with your audio or text. Please try again"
        else:
            flags = ["--force-overwrite"]
            if session["config"].get("--save-temps", False):
                flags.append("--save-temps")
            output_formats = []
            if session["config"].get("--closed-captioning", False):
                output_formats.append("srt")
            if session["config"].get("--text-grid", False):
                output_formats.append("TextGrid")
            if output_formats:
                flags.extend(("-o", ",".join(output_formats)))
            if session["text"].endswith("txt"):
                flags.append("--language")
                flags.append(session["config"]["lang"])
            timestamp = str(int(datetime.now().timestamp()))
            output_base = "aligned" + timestamp
            args = (
                ["readalongs", "align"]
                + flags
                + [
                    session["text"],
                    session["audio"],
                    os.path.join(session["temp_dir"], output_base),
                ]
            )
            LOGGER.warning(args)
            _, audio_ext = os.path.splitext(session["audio"])
            data = {"audio_ext": audio_ext, "base": output_base}
            if session["config"].get("show-log", False):
                log = run(args, capture_output=True, check=False)
                data["log"] = log
                log_lines = list(re.split(r"\r?\n", safe_decode(log.stdout)))
                log_lines.extend(list(re.split(r"\r?\n", safe_decode(log.stderr))))
                data["log_lines"] = [
                    re.sub(r"\x1b\[\d*m", "", line) for line in log_lines
                ]
            else:
                run(args, check=False)
            data["audio_path"] = os.path.join(
                session["temp_dir"], output_base, output_base + audio_ext
            )
            data["audio_fn"] = f"/file/{output_base}" + audio_ext
            data["text_path"] = os.path.join(
                session["temp_dir"], output_base, output_base + ".xml"
            )
            data["text_fn"] = f"/file/{output_base}" + ".xml"
            data["smil_path"] = os.path.join(
                session["temp_dir"], output_base, output_base + ".smil"
            )
            data["smil_fn"] = f"/file/{output_base}" + ".smil"
        return render_template("export.html", data=data)
    else:
        abort(404)


@app.route("/download/<string:base>", methods=["GET"])
def show_zip(base):
    files_to_download = os.listdir(os.path.join(session["temp_dir"], base))
    if (
        "temp_dir" not in session
        or not os.path.exists(session["temp_dir"])
        or not files_to_download
        or not any(x.startswith("aligned") for x in files_to_download)
    ):
        return abort(
            404, "Nothing to download. Please go to Step 1 of the Read Along Studio"
        )

    data = io.BytesIO()
    with ZipFile(data, mode="w") as z:
        for fname in files_to_download:
            path = os.path.join(session["temp_dir"], base, fname)
            if fname.startswith("aligned") or fname == "index.html":
                z.write(path, fname)
    data.seek(0)

    if not data:
        return abort(400, "Invalid zip file")

    return send_file(
        data,
        mimetype="application/zip",
        as_attachment=True,
        attachment_filename="data_bundle.zip",
    )


@app.route("/file/<string:fname>", methods=["GET"])
def return_temp_file(fname):
    fn, _ = os.path.splitext(fname)
    LOGGER.warning(session["temp_dir"])
    path = os.path.join(session["temp_dir"], fn, fname)
    if os.path.exists(path):
        return send_file(path)
    else:
        abort(404, "Sorry, we couldn't find that file.")
