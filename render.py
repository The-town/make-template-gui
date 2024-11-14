from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")


env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape()
)


def get_render_text(template_file: str, context: dict) -> str:
    template = env.get_template(template_file)
    return template.render(context)
