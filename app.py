from sites.chrono import chrono_crawl
from sites.govberg import govberg_crawl
from sites.watchquote import watchq_crawl


try:
    chrono_crawl()
except Exception as e:
    print(e)
    pass

try:
    govberg_crawl()
except Exception as e:
    print(e)
    pass

try:
    watchq_crawl()
except Exception as e:
    print(e)
    pass

