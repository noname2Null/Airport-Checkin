import requests
import json
import os
import time

requests.packages.urllib3.disable_warnings()

SCKEY = os.environ.get('SCKEY', '')
TG_BOT_TOKEN = os.environ.get('TGBOT', '')
TG_USER_ID = os.environ.get('TGUSERID', '')

def checkin():
    email = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')
    base_url = os.environ.get('BASE_URL').rstrip('/')  # 自动去掉多余的 /

    if not all([email, password, base_url]):
        return "❌ 环境变量 EMAIL/PASSWORD/BASE_URL 未设置完整！"

    session = requests.session()
    session.get(base_url, verify=False, timeout=15)

    # ==================== 登录 ====================
    login_url = base_url + '/auth/login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': base_url + '/auth/login'
    }
    data = {
        'email': email,
        'passwd': password,
        'code': ''          # 你的机场登录页没有验证码，留空即可
    }

    login_resp = session.post(login_url, data=data, headers=headers, verify=False, timeout=15)
    print(f"🔑 登录状态码: {login_resp.status_code}")
    print(f"🔑 登录返回内容: {login_resp.text[:800]}")   # 打印前800字符便于调试

    # ==================== 签到 ====================
    checkin_url = base_url + '/user/checkin'
    headers['Referer'] = base_url + '/user'
    checkin_resp = session.post(checkin_url, headers=headers, verify=False, timeout=15)

    print(f"📌 签到状态码: {checkin_resp.status_code}")
    print(f"📌 签到返回内容: {checkin_resp.text[:800]}")

    try:
        result = json.loads(checkin_resp.text)
        msg = result.get('msg', '未知返回')
        print(f"✅ 签到结果: {msg}")
        return msg
    except json.JSONDecodeError:
        return f"❌ 签到返回非JSON（可能是登录失败或接口变动）"

result = checkin()

# ==================== 推送 ====================
if SCKEY:
    try:
        requests.get(f'https://sctapi.ftqq.com/{SCKEY}.send?title=机场签到&desp={result}')
    except:
        pass

if TG_USER_ID and TG_BOT_TOKEN:
    try:
        requests.get(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage?chat_id={TG_USER_ID}&text={result}&disable_web_page_preview=True')
    except:
        pass
