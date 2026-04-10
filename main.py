import cloudscraper
import json
import os
from datetime import datetime

# ====================== 配置 ======================
SCKEY = os.environ.get('SCKEY', '')
TG_BOT_TOKEN = os.environ.get('TGBOT', '')
TG_USER_ID = os.environ.get('TGUSERID', '')
SHOP_ID = os.environ.get('SHOP_ID')          # 必须设置为 8

def push(title, desp):
    scraper = cloudscraper.create_scraper()
    if SCKEY:
        try:
            url = f"https://sctapi.ftqq.com/{SCKEY}.send"
            scraper.get(url, params={'title': title, 'desp': desp}, timeout=10)
        except:
            pass
    if TG_BOT_TOKEN and TG_USER_ID:
        try:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
            text = f"{title}\n\n{desp}"
            scraper.get(url, params={'chat_id': TG_USER_ID, 'text': text, 'disable_web_page_preview': True}, timeout=10)
        except:
            pass

def checkin(scraper, base_url, email, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': base_url + '/auth/login'
    }
    # 登录
    login_resp = scraper.post(base_url + '/auth/login', data={'email': email, 'passwd': password, 'code': ''}, headers=headers, timeout=15)
    # 签到
    checkin_resp = scraper.post(base_url + '/user/checkin', headers=headers, timeout=15)

    try:
        result = json.loads(checkin_resp.text)
        msg = result.get('msg', '未知')
        return f"签到成功：{msg}"
    except:
        return "签到失败（可能登录未成功）"

def auto_buy(scraper, base_url):
    if not SHOP_ID:
        return "未设置 SHOP_ID，跳过购买"
    try:
        buy_resp = scraper.post(
            base_url + '/user/buy',
            data={'shop': SHOP_ID, 'coupon': ''},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            timeout=15
        )
        try:
            result = json.loads(buy_resp.text)
            msg = result.get('msg', buy_resp.text[:200])
            return msg
        except:
            return buy_resp.text[:200]
    except Exception as e:
        return f"购买异常: {e}"

# ====================== 主程序 ======================
if __name__ == "__main__":
    email = os.environ.get('EMAIL')
    password = os.environ.get('PASSWORD')
    base_url = os.environ.get('BASE_URL').rstrip('/')

    scraper = cloudscraper.create_scraper()

    sign_result = checkin(scraper, base_url, email, password)
    buy_result = auto_buy(scraper, base_url)

    # 构建你想要的推送标题
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sign_ok = "√" if "成功" in sign_result else "×"
    
    # 购买状态判断（更精准）
    if "成功" in buy_result or "订单" in buy_result or "已购买" in buy_result:
        buy_ok = "√"
    elif "间隔" in buy_result or "24" in buy_result or "不足" in buy_result or "冷却" in buy_result:
        buy_ok = "×(间隔不足)"
    else:
        buy_ok = "×"

    title = f"签到{sign_ok} 购买{buy_ok} {now}"
    desp = f"签到结果：{sign_result}\n购买结果：{buy_result}\n执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print(f"\n🚀 最终推送标题：{title}")
    print(desp)
    push(title, desp)
