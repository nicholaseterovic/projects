import inspect
import typing as tp
from dash import html as dhc
from html.parser import HTMLParser

class DashHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs) -> object:
        super().__init__(*args, **kwargs)
        self._stack = []
        self.dash_object:tp.List[object] = []

    @staticmethod
    def get_dash_class(tag:str) -> object:
        attr = tag.title()
        if hasattr(dhc, attr):
            return getattr(dhc, attr)
        raise ValueError(f"Unable to find Dash class for {attr}")        

    def handle_starttag(self, tag:str, attrs:tp.List[tp.Tuple[str, str]]) -> None:
        dash_class = DashHTMLParser.get_dash_class(tag)
        dash_attrs = {}

        if attrs:
            named_dash_attrs = list(inspect.signature(dash_class.__init__).parameters)[1:-1]
            lower_named_dash_attrs = {n.lower():n for n in named_dash_attrs}
            for attr_name, attr_value in attrs:
                lower_attr_name = attr_name.lower()
                if lower_attr_name == 'class':
                    dash_attrs['className'] = attr_value
                elif lower_attr_name == 'style':
                    style_dict = {}
                    for style in attr_value.split(';'):
                        style_key, style_value = style.split(':')
                        style_dict[style_key] = style_value
                    dash_attrs['style'] = style_dict
                elif lower_attr_name in ('n_clicks', 'n_clicks_timestamp'):
                    dash_attrs[lower_attr_name] = int(attr_value)
                elif lower_attr_name in lower_named_dash_attrs:
                    dash_attrs[lower_named_dash_attrs[lower_attr_name]] = attr_value
                else:
                    dash_attrs[attr_name] = attr_value
        
        # Create the real tag
        dash_tag = dash_tag_class(**dash_attrs)(**dash_attrs)
        self._stack.append(dash_tag)

    def handle_endtag(self, tag:str) -> None:
        dash_class = self.get_dash_class(tag=tag)
        dash_tag = self._stack.pop()
        if type(dash_tag) is not dash_class:
            raise ValueError(f'Malformed HTML')

        # Final Tag
        if not self._stack:
            self.dash_object = dash_tag
            return

        if type(self._stack[-1].children) is not list:
            self._stack[-1].children = []

        self._stack[-1].children.append(dash_tag)

    def handle_data(self, data) -> None:
        if type(self._stack[-1].children) is not list:
            self._stack[-1].children = []
        self._stack[-1].children.append(data)
