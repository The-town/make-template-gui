from jinja2 import Environment, FileSystemLoader, select_autoescape
import component


env = Environment(
    loader=FileSystemLoader("test_app"),
    autoescape=select_autoescape()
)

template = env.get_template("mytemplate.txt")

window = component.Window()
window.root.mainloop()
