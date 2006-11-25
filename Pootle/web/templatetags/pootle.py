from django.template import Library,Context,Node,loader,TemplateSyntaxError

register = Library()

class ItemNode(Node):
    def __init__(self):
        pass

    def render(self, context):
        t = loader.get_template('node_item.html')
        return t.render(context)

def itemnode(parser, token):
    return ItemNode()
itemnode = register.tag('itemnode',itemnode)
