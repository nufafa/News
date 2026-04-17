# RSS 信息源配置

CATEGORIES = [
    {
        "name": "互联网资讯",
        "description": "整合互联网资讯媒体，偏重于前端科技、电子硬件、手机应用。",
        "sources": [
            {"name": "36Kr", "url": "https://rss.aishort.top/?type=36kr"},
            {"name": "虎嗅网", "url": "https://rss.aishort.top/?type=huxiu"},
            {"name": "艾瑞网", "url": "https://rss.aishort.top/?type=iresearch"},
            {"name": "爱范儿", "url": "https://rss.aishort.top/?type=AppSolution"},
            {"name": "效率火箭", "url": "https://rss.aishort.top/?type=xlrocket"},
        ]
    },
    {
        "name": "奇思妙想",
        "description": "每天吸收些稀奇古怪的知识，期待引发后续的灵机一动。",
        "sources": [
            {"name": "果壳网", "url": "https://rss.aishort.top/?type=guokr"},
            {"name": "少数派", "url": "https://rss.aishort.top/?type=sspai"},
            {"name": "知乎想法热榜", "url": "https://rss.aishort.top/?type=zhihu"},
        ]
    }
]

# 输出目录
OUTPUT_DIR = "docs"

# 最多显示每个源的文章数量
MAX_ARTICLES_PER_SOURCE = 10

# 请求超时（秒）
REQUEST_TIMEOUT = 15
