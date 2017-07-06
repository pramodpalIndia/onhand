from django import template

register = template.Library

# @register.filter(name='add_attributes')
# def add_attributes(field, css):
#     attrs = {}
#     definition = css.split(',')
#
#     for d in definition:
#         if ':' not in d:
#             attrs['class'] = d
#         else:
#             t, v = d.split(':')
#             attrs[t] = v
#
#     return field.as_widget(attrs=attrs)



# class UserDisplayNode(template.Node):
#
#     def __init__(self, user, as_var=None):
#         self.user_var = template.Variable(user)
#         self.as_var = as_var
#
#     def render(self, context):
#         user = self.user_var.resolve(context)
#
#         display = user_display(user)
#
#         if self.as_var:
#             context[self.as_var] = display
#             return ""
#         return display
#
#
# @register.tag(name="user_display")
# def do_user_display(parser, token):
#     """
#     Example usage::
#
#         {% user_display user %}
#
#     or if you need to use in a {% blocktrans %}::
#
#         {% user_display user as user_display %}
#         {% blocktrans %}
#         {{ user_display }} has sent you a gift.
#         {% endblocktrans %}
#
#     """
#     bits = token.split_contents()
#     if len(bits) == 2:
#         user = bits[1]
#         as_var = None
#     elif len(bits) == 4:
#         user = bits[1]
#         as_var = bits[3]
#     else:
#         raise template.TemplateSyntaxError(
#             "'%s' takes either two or four arguments" % bits[0])
#
#     return UserDisplayNode(user, as_var)


# @register.tag(self)
# def show_plans(plan):
#     plans = plan_display()
#     return {'plans': plans}



# class PlanDisplayNode(template.Node):
#
#     def __init__(self, plan, as_var=None):
#         self.plan_var = template.Variable(plan)
#         self.as_var = as_var
#
#     def render(self, context):
#         plan = self.plan_var.resolve(context)
#         display = plan_display(plan)
#         if self.as_var:
#             context[self.as_var] = display
#             return ""
#         return display



# @register.simple_tag
# def do_plan_display(parser, token):
#
#     bits = token.split_contents()
#     if len(bits) == 2:
#         plan = bits[1]
#         as_var = None
#     elif len(bits) == 4:
#         plan = bits[1]
#         as_var = bits[3]
#     else:
#         raise template.TemplateSyntaxError(
#             "'%s' takes either two or four arguments" % bits[0])
#
#     return PlanDisplayNode(plan, as_var)
