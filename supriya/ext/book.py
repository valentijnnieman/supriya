import base64
import pathlib
import pickle
import textwrap

from docutils.nodes import FixedTextElement, General, SkipNode
from uqbar.book.extensions import Extension
from uqbar.strings import normalize

from supriya.ext import websafe_audio
from supriya.io import Player


class PlayerExtension(Extension):
    def setup(self, console, monkeypatch):
        monkeypatch.setattr(
            Player,
            "__call__",
            lambda self: console.push_proxy(
                RenderableProxy(self.renderable, self.render_kwargs)
            ),
        )

    def setup_sphinx(self, app):
        RenderableProxy.setup_sphinx(app)


class RenderableProxy:

    template = normalize(
        """
        """
    )

    class render_block(General, FixedTextElement):
        pass

    def __init__(self, renderable, render_kwargs):
        self.renderable = pickle.loads(pickle.dumps(renderable))
        self.render_kwargs = pickle.loads(pickle.dumps(render_kwargs))

    def to_docutils(self):
        code = "\n".join(
            textwrap.wrap(
                base64.b64encode(
                    pickle.dumps((self.renderable, self.render_kwargs))
                ).decode()
            )
        )
        node = self.render_block(code, code)
        return [node]

    @classmethod
    def setup_sphinx(cls, app):
        app.add_node(
            cls.render_block,
            html=[cls.visit_render_block_html, None],
            latex=[cls.visit_render_block_latex, None],
            text=[cls.visit_render_block_text, cls.depart_render_block_text],
        )

    @classmethod
    def render(cls, node, output_path):
        output_path.mkdir(exist_ok=True)
        renderable, render_kwargs = pickle.loads(
            base64.b64decode("".join(node[0].split()))
        )
        return websafe_audio(
            renderable.__render__(render_directory_path=output_path, **render_kwargs)
        )

    @staticmethod
    def visit_render_block_html(self, node):
        absolute_file_path = RenderableProxy.render(
            node, pathlib.Path(self.builder.outdir) / "_images"
        )
        relative_file_path = (
            pathlib.Path(self.builder.imgpath) / absolute_file_path.name
        )
        result = RenderableProxy.template.format(file_path=relative_file_path)
        self.body.append(result)
        raise SkipNode

    @staticmethod
    def visit_render_block_latex(self, node):
        raise SkipNode

    @staticmethod
    def depart_render_block_text(self, node):
        self.end_state(wrap=False)

    @staticmethod
    def visit_render_block_text(self, node):
        self.new_state()