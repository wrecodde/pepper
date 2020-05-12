
import tornado.web
import tornado.httpserver
import tornado.httpclient

import io, os, json
import secrets, random

import requests


secret_key = os.getenv('SECRET_KEY')

class BaseHandler(tornado.web.RequestHandler):
    pass
    
class IndexPage(BaseHandler):
    def get(self):
       self.render('index.html')

class AboutPage(BaseHandler):
    def get(self):
        self.render('about.html')

class PaymentsPage(BaseHandler):
    def get(self):
        context = {
            'page': 'payment',
            'status': 'failed'
        }
        self.render('pay.html', context=context)
    
    def post(self):
        reference = self.get_argument('reference')
        request = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers={
                'Authorization': f'Bearer {secret_key}'
            }
        )
        context = { 'status': 'success'}
        
        if request.status_code == 200:
            response = json.loads(request.text)
            if response['data']['status'] == 'success':
                self.write(json.dumps(context))
            else:
                context['status'] = 'failed'
                self.write(json.dumps(context))
        else:
            context['status'] = 'failed'
            self.write(json.dumps(context))

class ThankYouPage(BaseHandler):
    def get(self):
        status = self.get_argument('status')
        print(status)
        self.render('thanks.html', status=status)


from tornado.options import define
define("port", default=3309, type=int)

handlers = [
    (r"/", IndexPage),
    (r"/about", AboutPage),
    (r"/pay", PaymentsPage),
    (r"/thanks", ThankYouPage),
]

# switch debug mode on or off
try:
    var = os.environ['APP_STAGE']
    prod = True if var == 'PROD' else False
except:
    prod = False


settings = dict(
    debug = False if prod else True,
    cookie_secret = secrets.token_hex(16),
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    autoescape = None,
)

app = tornado.web.Application(handlers, **settings)
def start():
    try:
        tornado.options.parse_command_line()
        port = tornado.options.options.port
        server = tornado.httpserver.HTTPServer(app)
        server.listen(port)
        
        start_msg = f"App server started. Port {port}"
        print('\n' + '=' * len(start_msg) + '\n' \
            + start_msg + '\n' + '=' * len(start_msg))
        
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        stop_msg = "Stopping app server"
        print('\n' + '=' * len(stop_msg) + '\n' \
            + stop_msg + '\n' + '=' * len(stop_msg))
        import sys
        sys.exit()

if __name__ == "__main__":
    start()
