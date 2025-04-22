import requests
from zhconv import convert
from ics import Calendar
from datetime import datetime, timedelta
import os
from dateutil.relativedelta import relativedelta

def download_ics(year):
    url = f"https://gcatholic.org/calendar/ics/{year}-zt-General-D.ics?v=3"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'  # 强制 UTF-8 解码
        response.raise_for_status()
        simplified = convert(response.text, 'zh-cn')
        simplified = simplified.replace('CHARSET=UTF-8', 'CHARSET=UTF-8')  # 确保编码声明
        print(f"下载 {year} 年日历成功（长度: {len(simplified)} 字符）")
        return simplified
    except Exception as e:
        print(f"下载 {year} 年日历失败: {e}")
        return None

def filter_events(cal, start_date, end_date):
    filtered = Calendar()
    for event in cal.events:
        event_start = event.begin.datetime.date() if hasattr(event.begin, 'datetime') else event.begin.date()
        if start_date <= event_start <= end_date:
            filtered.events.add(event)
    return filtered

def main():
    today = datetime.now().date()
    start_date = today.replace(day=1)
    end_date = (start_date + relativedelta(months=12)).replace(day=1) - timedelta(days=1)
    
    years = {start_date.year, end_date.year}
    all_events = Calendar()

    for year in years:
        ics_content = download_ics(year)
        if not ics_content:
            continue

        try:
            cal = Calendar(ics_content)
            filtered_cal = filter_events(cal, start_date, end_date)
            all_events.events.update(filtered_cal.events)
            print(f"合并 {year} 年事件成功（保留 {len(filtered_cal.events)} 个事件）")
        except Exception as e:
            print(f"处理 {year} 年日历时出错: {e}")

    output_dir = "calendars"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "latest_calendar.ics")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(all_events.serialize())
    print(f"文件已保存至 {output_path}（总事件数: {len(all_events.events)}）")

if __name__ == "__main__":
    main()