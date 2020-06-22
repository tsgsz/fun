CITY_DICT = {
    '北京': 'bj',
    '成都': 'cd',
    '重庆': 'cq',
    '长沙': 'cs',
    '东莞': 'dg',
    '大连': 'dl',
    '佛山': 'fs',
    '广州': 'gz',
    '杭州': 'hz',
    '合肥': 'hf',
    '济南': 'jn',
    '南京': 'nj',
    '青岛': 'qd',
    '上海': 'sh',
    '深圳': 'sz',
    '苏州': 'su',
    '沈阳': 'sy',
    '天津': 'tj',
    '武汉': 'wh',
    '厦门': 'xm',
    '烟台': 'yt',
}

CITY_CODE_DICT = {
    'bj': '北京',
    'cd': '成都',
    'cq': '重庆',
    'cs': '长沙',
    'dg': '东莞',
    'dl': '大连',
    'fs': '佛山',
    'gz': '广州',
    'hz': '杭州',
    'hf': '合肥',
    'jn': '济南',
    'nj': '南京',
    'qd': '青岛',
    'sh': '上海',
    'sz': '深圳',
    'su': '苏州',
    'sy': '沈阳',
    'tj': '天津',
    'wh': '武汉',
    'xm': '厦门',
    'yt': '烟台',
}

def city_to_city_code(city):
    return CITY_DICT[city]

def city_code_to_city(city_code):
    return CITY_CODE_DICT[city_code]