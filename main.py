import cloudscraper
import json
import os
from datetime import datetime

# ====================== 配置 ======================
SCKEY = os.environ.get('SCKEY', '')
TG_BOT_TOKEN = os.environ.get('TGBOT', '')
TG_USER_ID = os.environ.get('TGUSERID', '')
SHOP_ID = os.environ.get('SHOP_ID')          # ← 必须设置！见下方说明

def push(title, desp):
    if SCKEY:
        try:
            requests_url = f"https://sctapi.ftqq.com/{SCKEY}.send"
            payload = {'title': title, 'desp': desp}
            cloudscraper.create_scraper().get(requests_url, params=payload, timeout=10)
        except:
            pass
    if TG_BOT_TOKEN and TG_USER_ID:
        try:
            tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
            payload = {'chat_id': TG_USER_ID, 'text': f"{title}\n\n{desp}", 'disable_web_page_preview': True}
            cloudscraper.create_scraper().get(tg_url, params=payload, timeout=10)
        except:
            pass

def checkin(scraper, base_url, email, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Referer': base_url + '/auth/login'
    }
    # 登录
    login_url = base_url + '/auth/login'
    data = {'email': email, 'passwd': password, 'code': ''}
    login_resp = scraper.post(login_url, data=data, headers=headers, timeout=15)
    print(f"🔑 登录状态码: {login_resp.status_code}")

    # 签到
    checkin_url = base_url + '/user/checkin'
    headers['Referer'] = base_url + '/user'
    checkin_resp = scraper.post(checkin_url, headers=headers, timeout=15)
    print(f"📌 签到状态码: {checkin_resp.status_code}")

    try:
        result = json.loads(checkin_resp.text)
        msg = result.get('msg', '未知')
        print(f"✅ 签到结果: {msg}")
        return f"签到成功：{msg}"
    except:
        print(f"❌ 签到返回非JSON：{checkin_resp.text[:500]}")
        return "签到失败（可能登录未成功）"

def auto_buy(scraper, base_url):
    if not SHOP_ID:
        return "未设置 SHOP_ID，跳过购买"
    try:
        buy_url = base_url + '/user/buy'
        data = {'shop': SHOP_ID, 'coupon': ''}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        buy_resp = scraper.post(buy_url, data=data, headers=headers, timeout=15)
        print(f"🛒 购买状态码: {buy_resp.status_code}")
        print(f"🛒 购买返回: {buy_resp.text[:600]}")

        try:
            result = json.loads(buy_resp.text)
            msg = result.get('msg', '未知')
            return msg
        except:
            return "购买返回非JSON"
    except Exception as e:
        return f"购买异常: {e}"

# ====================== 主程序 ======================
if __name__ == "__main__":
    email = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')
    base_url = os.environ.get('BASE_URL').rstrip('/')

    scraper = cloudscraper.create_scraper()   # 关键：绕过 Cloudflare

    sign_result = checkin(scraper, base_url, email, password)
    buy_result = auto_buy(scraper, base_url)

    # 构建推送标题和内容
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sign_ok = "√" if "成功" in sign_result else "×"
    buy_ok = "√" if "成功" in buy_result or "已购买" in buy_result else "×(间隔不足)" if "间隔" in buy_result or "不足" in buy_result else "×"
    title = f"签到{sign_ok}购买{buy_ok} {now}"
    desp = f"签到结果：{sign_result}\n购买结果：{buy_result}\n执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print(f"\n🚀 最终推送标题：{title}")
    print(desp)
    push(title, desp)
