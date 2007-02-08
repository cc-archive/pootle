from django.template import Library,Context,Node,loader,TemplateSyntaxError

register = Library()

class ItemNode(Node):
    def __init__(self, template_name):
        self.template = "node_item_%s.html" % template_name

    def render(self, context):
        t = loader.get_template(self.template)
        return t.render(context)

def itemnode(parser, token):
    bits = token.split_contents()
    return ItemNode(bits[1])
itemnode = register.tag('itemnode',itemnode)
