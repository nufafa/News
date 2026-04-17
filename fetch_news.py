#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import feedparser
import requests
import os
import json
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import CATEGORIES, OUTPUT_DIR, MAX_ARTICLES_PER_SOURCE, REQUEST_TIMEOUT

# 北京时间
CST = timezone(timedelta(hours=8))

def fetch_feed(source):
    """抓取单个RSS源"""
    name = source["name"]
    url = source["url"]
    articles = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.encoding = "utf-8"
        feed = feedparser.parse(resp.text)

        for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
            # 解析时间
            pub_time = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(CST)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).astimezone(CST)
            else:
                pub_time = datetime.now(CST)

            # 摘要
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            # 清理HTML标签（简单处理）
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = re.sub(r'\s+', ' ', summary).strip()
            if len(summary) > 150:
                summary = summary[:150] + "..."

            articles.append({
                "title": entry.get("title", "无标题").strip(),
                "link": entry.get("link", ""),
                "pub_time": pub_time,
                "pub_time_str": pub_time.strftime("%Y-%m-%d %H:%M"),
                "source": name,
                "summary": summary,
            })

        print(f"  ✓ {name}：获取 {len(articles)} 篇文章")
    except Exception as e:
        print(f"  ✗ {name}：抓取失败 - {e}")

    return articles


def fetch_all():
    """并发抓取所有源"""
    all_articles_by_category = []

    for category in CATEGORIES:
        print(f"\n[{category['name']}]")
        cat_articles = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_feed, source): source for source in category["sources"]}
            for future in as_completed(futures):
                articles = future.result()
                cat_articles.extend(articles)

        # 按时间降序排列
        cat_articles.sort(key=lambda x: x["pub_time"], reverse=True)
        all_articles_by_category.append({
            "name": category["name"],
            "description": category["description"],
            "articles": cat_articles
        })

    return all_articles_by_category


def generate_markdown(data, date_str):
    """生成Markdown文件"""
    lines = [f"# 互联网新闻聚合 - {date_str}\n"]
    lines.append(f"> 生成时间：{datetime.now(CST).strftime('%Y-%m-%d %H:%M')} 北京时间\n\n")

    for category in data:
        lines.append(f"## {category['name']}\n")
        lines.append(f"> {category['description']}\n\n")

        if not category["articles"]:
            lines.append("_暂无文章_\n\n")
            continue

        for art in category["articles"]:
            lines.append(f"### [{art['title']}]({art['link']})\n")
            lines.append(f"**{art['pub_time_str']}** · {art['source']}\n\n")
            if art["summary"]:
                lines.append(f"{art['summary']}\n\n")
            lines.append("---\n\n")

    return "".join(lines)


def generate_html(data, date_str):
    """生成HTML页面"""
    now_str = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

    # 生成分类导航
    nav_items = ""
    for cat in data:
        anchor = cat["name"]
        nav_items += f'<a href="#{anchor}" class="nav-item">{anchor}</a>\n'

    # 生成文章内容
    content_html = ""
    for category in data:
        content_html += f'''
        <section id="{category["name"]}" class="category-section">
            <div class="category-header">
                <h2>{category["name"]}</h2>
                <p class="category-desc">{category["description"]}</p>
            </div>
            <div class="articles-grid">
        '''

        if not category["articles"]:
            content_html += '<p class="no-articles">暂无文章</p>'
        else:
            for art in category["articles"]:
                summary_html = f'<p class="article-summary">{art["summary"]}</p>' if art["summary"] else ""
                content_html += f'''
                <article class="article-card">
                    <div class="article-meta">
                        <span class="article-source">{art["source"]}</span>
                        <span class="article-time">{art["pub_time_str"]}</span>
                    </div>
                    <h3 class="article-title">
                        <a href="{art["link"]}" target="_blank" rel="noopener">{art["title"]}</a>
                    </h3>
                    {summary_html}
                </article>
                '''

        content_html += '</div></section>'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>互联网新闻聚合 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.6;
        }}

        /* 顶部导航 */
        header {{
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0,0,0,0.08);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 0 24px;
        }}

        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 56px;
        }}

        .site-title {{
            font-size: 18px;
            font-weight: 700;
            color: #1d1d1f;
            letter-spacing: -0.3px;
        }}

        .site-date {{
            font-size: 13px;
            color: #86868b;
        }}

        nav {{
            display: flex;
            gap: 4px;
        }}

        .nav-item {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            color: #1d1d1f;
            text-decoration: none;
            transition: background 0.2s;
            font-weight: 500;
        }}

        .nav-item:hover {{
            background: #f5f5f7;
        }}

        /* 主内容区 */
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 24px;
        }}

        /* 分类区块 */
        .category-section {{
            margin-bottom: 48px;
        }}

        .category-header {{
            margin-bottom: 20px;
        }}

        .category-header h2 {{
            font-size: 28px;
            font-weight: 700;
            color: #1d1d1f;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}

        .category-desc {{
            font-size: 15px;
            color: #86868b;
        }}

        /* 文章网格 */
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 16px;
        }}

        /* 文章卡片 */
        .article-card {{
            background: #fff;
            border-radius: 16px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid rgba(0,0,0,0.06);
        }}

        .article-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }}

        .article-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
        }}

        .article-source {{
            background: #f0f0f5;
            color: #6e6e73;
            font-size: 12px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 10px;
        }}

        .article-time {{
            font-size: 12px;
            color: #86868b;
        }}

        .article-title {{
            font-size: 16px;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 8px;
        }}

        .article-title a {{
            color: #1d1d1f;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .article-title a:hover {{
            color: #0071e3;
        }}

        .article-summary {{
            font-size: 14px;
            color: #6e6e73;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        /* 页脚 */
        footer {{
            text-align: center;
            padding: 32px 24px;
            color: #86868b;
            font-size: 13px;
            border-top: 1px solid rgba(0,0,0,0.06);
        }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .header-inner {{ flex-direction: column; height: auto; padding: 12px 0; gap: 8px; }}
            nav {{ flex-wrap: wrap; justify-content: center; }}
            .articles-grid {{ grid-template-columns: 1fr; }}
            .category-header h2 {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <div>
                <div class="site-title">📰 互联网新闻聚合</div>
            </div>
            <nav>
                {nav_items}
            </nav>
            <div class="site-date">更新于 {now_str}</div>
        </div>
    </header>

    <main>
        {content_html}
    </main>

    <footer>
        <p>互联网新闻聚合 · {date_str} · 数据来源：36Kr / 虎嗅 / 少数派 等</p>
    </footer>
</body>
</html>'''

    return html


def save_outputs(data, date_str):
    """保存MD和HTML文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    md_content = generate_markdown(data, date_str)
    html_content = generate_html(data, date_str)

    # 按日期保存
    md_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    html_path = os.path.join(OUTPUT_DIR, f"{date_str}.html")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 同时更新 latest 文件
    latest_md = os.path.join(OUTPUT_DIR, "latest.md")
    latest_html = os.path.join(OUTPUT_DIR, "index.html")

    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(latest_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    return md_path, html_path


def main():
    date_str = datetime.now(CST).strftime("%Y-%m-%d")
    print(f"开始抓取新闻聚合 [{date_str}]")
    print("=" * 50)

    data = fetch_all()

    print("\n生成输出文件...")
    md_path, html_path = save_outputs(data, date_str)

    # 统计
    total = sum(len(cat["articles"]) for cat in data)
    print(f"\n✅ 完成！共抓取 {total} 篇文章")
    print(f"   Markdown: {md_path}")
    print(f"   HTML:     {html_path}")
    print(f"   最新:     {OUTPUT_DIR}/index.html")


if __name__ == "__main__":
    main()
