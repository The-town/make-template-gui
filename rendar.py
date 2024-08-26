from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader("test_app"),
    autoescape=select_autoescape()
)


def get_render_text(template_file: str, context: dict) -> str:
    template = env.get_template(template_file)
    # print(template.render({"A": "りんご", "B": "みかん"}))
    return template.render(context)

