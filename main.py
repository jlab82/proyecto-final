#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        all_messages = Message.query(Message.deleted==False).fetch()

        context = {
            "all_messages": all_messages,
        }

        return self.render_template("index.html", params=context)


class MessageCreateHandler(BaseHandler):
    def get(self):
        return self.render_template("message-create.html")

    def post(self):
        # get inputs values
        user = users.get_current_user()
        user_name = self.request.get("name")
        user_text = self.request.get("text")
        user_email = user.email()

        if not user_name:
            user_name = "Anonymous"

        new_message = Message(name=user_name, text=user_text, email=user_email)
        new_message.put()

        return self.redirect_to('msg-list')


class MessageDetailsHandler(BaseHandler):
    def get(self, message_id):
        msg = Message.get_by_id(int(message_id))

        context = {
            "message": msg,
        }

        return self.render_template("message-details.html", params=context)


class MessageEditHandler(BaseHandler):
    def get(self, message_id):
        msg = Message.get_by_id(int(message_id))

        context = {
            "message": msg,
        }

        return self.render_template("message-edit.html", params=context)

    def post(self, message_id):
        # get inputs values
        user_name = self.request.get("name")
        user_text = self.request.get("text")
        user_email = self.request.get("email")

        msg = Message.get_by_id(int(message_id))
        msg.text = user_text
        msg.email = user_email
        msg.name = user_name

        msg.put()

        return self.redirect_to('msg-list')


class MessageDeleteHandler(BaseHandler):
    def get(self, message_id):
        msg = Message.get_by_id(int(message_id))

        context = {
            "message": msg,
        }

        return self.render_template("message-delete.html", params=context)

    def post(self, message_id):
        msg = Message.get_by_id(int(message_id))

        msg.deleted = True
        msg.put()

        return self.redirect_to('msg-list')


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="msg-list"),
    webapp2.Route('/message-create', MessageCreateHandler),
    webapp2.Route('/message/<message_id:\d+>/details', MessageDetailsHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', MessageEditHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', MessageDeleteHandler),
], debug=True)
