"""
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def hello(request):
    return HttpResponse('Hello, W')
"""


import json
from django.shortcuts import render
from django.views import generic
#from accounts.models import User
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib import messages
import requests
import jwt


LINE_CHANNEL_ID = "Udf51e6a017a9af79f53e6cea8490cd4b" # 自身のLINEチャンネルIDを入力
LINE_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET
REDIRECT_URL = settings.LINE_REDIRECT_URL

# ログインボタンをおく画面
class _(generic.TemplateView):
   template_name = 'lineapp/enter.html'

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['channel_id'] = LINE_CHANNEL_ID
       context['redirect_url'] = REDIRECT_URL
       context['random_state'] = "line1216" # 参照元ママ
       return context


# LINEloginのリダイレクト先
def line_login(request):
   context = {}
   # 認可コードを取得する
   request_code = request.GET.get("code")
   uri_access_token = "https://api.line.me/oauth2/v2.1/token"
   headers = {"Content-Type": "application/x-www-form-urlencoded"}
   data_params = {
       "grant_type": "authorization_code",
       "code": request_code,
       "redirect_uri": REDIRECT_URL,
       "client_id": LINE_CHANNEL_ID,
       "client_secret": LINE_CHANNEL_SECRET
   }

   # トークンを取得するためにリクエストを送る
   response_post = requests.post(uri_access_token, headers=headers, data=data_params)

   # 今回は"id_token"のみを使用する
   line_id_token = json.loads(response_post.text)["id_token"]

   # ペイロード部分をデコードすることで、ユーザ情報を取得する
   user_profile = jwt.decode(line_id_token,
                             LINE_CHANNEL_SECRET,
                             audience=LINE_CHANNEL_ID,
                             issuer='https://access.line.me',
                             algorithms=['HS256'])

   # LINE登録のユーザー情報を表示する場合は、contextに追加しておく
   context["user_profile"]=user_profile

   # LINEで取得した情報と、ユーザーデータベースを付け合わせ
   line_user, created = User.objects.get_or_create(email=user_profile["email"])

   if (created):
       line_user.username = user_profile['name']  # 例：ユーザーネームにLINEネームを反映
       line_user.save()
       messages.success(request, 'ユーザーを作成しました。ユーザー名：{}'.format(line_user.username))

   else:
       messages.warning(request, 'ログインしました。{}'.format(line_user.get_full_name()))

   # そのままログインさせる
   login(request, line_user, backend='django.contrib.auth.backends.ModelBackend')

   return render(request, "lineapp/line_success.html", context)