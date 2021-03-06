import subprocess
from xml.dom import minidom  # type: ignore

import uqbar.io
from IPython.core.display import display, display_svg  # type: ignore
from IPython.display import Audio  # type: ignore

from supriya.io import Grapher, Player


def load_ipython_extension(ipython):
    patch_grapher()
    patch_player()


def patch_grapher():
    def get_format(self):
        return "svg"

    def open_output_path(self, output_path):
        with output_path.open() as file_pointer:
            contents = file_pointer.read()
        delete_attributes = True
        document = minidom.parseString(contents)
        svg_element = document.getElementsByTagName("svg")[0]
        view_box = svg_element.getAttribute("viewBox")
        view_box = [float(_) for _ in view_box.split()]
        if delete_attributes:
            if svg_element.attributes.get("height", None):
                del (svg_element.attributes["height"])
            if svg_element.attributes.get("width", None):
                del (svg_element.attributes["width"])
        else:
            height = "{}pt".format(int(view_box[-1] * 0.6))
            width = "{}pt".format(int(view_box[-2] * 0.6))
            svg_element.setAttribute("height", height)
            svg_element.setAttribute("width", width)
        svg_element.setAttribute("preserveAspectRatio", "xMinYMin")
        contents = document.toprettyxml()
        display_svg(contents, raw=True)

    Grapher.get_format = get_format
    Grapher.open_output_path = open_output_path


def patch_player():
    def render(self):
        output_path = self.renderable.__render__(**self.render_kwargs)
        # HTML5 Audio element can't display AIFFs properly, but can WAVE:
        if uqbar.io.find_executable("ffmpeg") and output_path.suffix.startswith(".aif"):
            new_output_path = output_path.with_suffix(".wav")
            command = "ffmpeg -i {} {}".format(output_path, new_output_path)
            exit_code = subprocess.call(command, shell=True)
            if not exit_code:
                output_path = new_output_path
        # Convert to MP3 if possible for smaller file sizes:
        if uqbar.io.find_executable("lame"):
            new_output_path = output_path.with_suffix(".mp3")
            command = "lame -V2 {} {}".format(output_path, new_output_path)
            exit_code = subprocess.call(command, shell=True)
            if not exit_code:
                output_path = new_output_path
        return output_path

    def open_output_path(self, output_path):
        display(Audio(filename=str(output_path)))

    Player.open_output_path = open_output_path
    Player.render = render
