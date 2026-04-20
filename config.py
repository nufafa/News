# RSS 信息源配置

CATEGORIES = [
    {
        "name": "互联网资讯",
        "description": "整合互联网资讯媒体，偏重于前端科技、电子硬件、手机应用。",
        "sources": [
            {"name": "《联合早报》-国际-即时", "url": "https://plink.anyfeeder.com/zaobao/realtime/world"},
            {"name": "极客公园", "url": "http://www.geekpark.net/rss"},
            {"name": "ZAKER 精读新闻", "url": "https://rsshub.app/zaker/focusread"},
            {"name": "36氪", "url": "https://www.36kr.com/feed"},
            {"name": "今日话题 - 雪球", "url": "https://plink.anyfeeder.com/xueqiu/hot"},
        ]
    },
    {
        "name": "奇思妙想",
        "description": "每天吸收些稀奇古怪的知识，期待引发后续的灵机一动。",
        "sources": [
            {"name": "知乎日报", "url": "https://plink.anyfeeder.com/zhihu/daily"},
            {"name": "酷 壳 – CoolShell", "url": "http://coolshell.cn/feed"},
            {"name": "少数派", "url": "https://sspai.com/feed"},
        ]
    }
]

# 输出目录
OUTPUT_DIR = "docs"

# 最多显示每个源的文章数量
MAX_ARTICLES_PER_SOURCE = 10

# 请求超时（秒）
REQUEST_TIMEOUT = 15
