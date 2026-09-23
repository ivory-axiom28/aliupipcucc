from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import os
import json
from datetime import datetime, timezone, timedelta

from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest, UpdateDomainRecordRequest

URL = "https://api.uouin.com/cloudflare.html"
OUTPUT_FILE = "aliupipcucc.txt"

# 阿里云配置（从环境变量读取）
ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
DOMAIN_NAME = os.environ.get('ALIYUN_DOMAIN_NAME')   # 例如 example.com
RR = os.environ.get('ALIYUN_RR')                     # 主机记录，例如 www 或 @
RECORD_TYPE = os.environ.get('ALIYUN_RECORD_TYPE', 'A')

def get_beijing_time():
    """获取当前北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_time = utc_now.astimezone(timezone(timedelta(hours=8)))
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

def fetch_telecom_ips():
    print(f"{get_beijing_time()} - 开始提取联通IP...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    
    # 使用随机延迟3-5秒
    random_delay = random.uniform(3, 5)
    print(f"等待页面加载，随机延迟 {random_delay:.2f} 秒")
    time.sleep(random_delay)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    ips = []
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2 and cols[0].get_text(strip=True) == "联通":
            ips.append(cols[1].get_text(strip=True))
            break
    
    # 只保存IP地址，不添加任何注释
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
      f.write("\n".join(ips))
    
    print(f"{get_beijing_time()} - 提取完成，共 {len(ips)} 个联通 IP。已保存到 {OUTPUT_FILE}")

def update_aliyun_dns():
    """读取文件中的第一个 IP 并更新到阿里云 DNS"""
    print(f"{get_beijing_time()} - 开始更新阿里云DNS...")

    # 1. 读取提取到的第一个 IP
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            new_ip = f.read().strip().split('\n')[0].strip()
    except FileNotFoundError:
        print(f"错误：未找到文件 {OUTPUT_FILE}")
        return

    if not new_ip:
        print("错误：文件中没有找到有效的 IP 地址")
        return

    print(f"准备将 {RR}.{DOMAIN_NAME} 的 {RECORD_TYPE} 记录更新为: {new_ip}")

    # 2. 初始化阿里云客户端
    client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, 'cn-hangzhou')

    # 3. 查询现有解析记录，获取 RecordId
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_DomainName(DOMAIN_NAME)
    request.set_RRKeyWord(RR)
    request.set_Type(RECORD_TYPE)
    request.set_accept_format('json')

    try:
        response = client.do_action_with_exception(request)
        result = json.loads(response)
        records = result.get('DomainRecords', {}).get('Record', [])
    except Exception as e:
        print(f"查询解析记录失败: {e}")
        return

    if not records:
        print(f"错误：未找到 {RR}.{DOMAIN_NAME} 的 {RECORD_TYPE} 记录，请先在阿里云DNS控制台手动添加")
        return

    record = records[0]
    record_id = record['RecordId']
    current_ip = record['Value']

    if current_ip == new_ip:
        print(f"IP 未变化 ({current_ip})，无需更新")
        return

    # 4. 更新解析记录
    update_request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    update_request.set_RecordId(record_id)
    update_request.set_RR(RR)
    update_request.set_Type(RECORD_TYPE)
    update_request.set_Value(new_ip)
    update_request.set_TTL(600)
    update_request.set_accept_format('json')

    try:
        update_response = client.do_action_with_exception(update_request)
        print(f"{get_beijing_time()} - DNS 记录更新成功！{RR}.{DOMAIN_NAME} -> {new_ip}")
    except Exception as e:
        print(f"更新 DNS 记录失败: {e}")

if __name__ == "__main__":
    fetch_telecom_ips()
    update_aliyun_dns()
