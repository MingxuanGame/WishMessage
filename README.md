## Wish Message

在特定的日期向玩家展示节日及其祝语

支持中国农历以及本月第几个星期几等日期

为了表达方便，“本月第几个星期几”下文叫做**周日次**

#### 依赖

| 包名称      | 要求    | 安装命令                       |
| ----------- | ------- | ------------------------------ |
| mcdreforged | > =2.0.0 | pip install mcdreforged>=2.0.0 |
| borax       | ~=3.4.4 | pip install ~=3.4.4            |

#### 命令

`!!wish`显示今天的祝福语

#### 自定义节日

所有的节日都在`config/wish_message/wish_days.json`中，每一个节日的格式如下

| 键      | 值类型                                              | 描述                                                         |
| ------- | --------------------------------------------------- | ------------------------------------------------------------ |
| name    | 字符串                                              | 节日的名称                                                   |
| type    | 字符串（Solar/Lunar/Week）                          | 节日日期的类型（分别是公历，农历，周日次）                   |
| date    | 列表（2个：月，日/3个：月，本月第几个星期，星期几） | 节日的日期（2个元素是公历农历，3个元素是周日次，星期几的映射表见下文） |
| message | 字符串或列表                                        | 向玩家展示的祝福语（如果是多条祝福语的列表则随机抽取）       |

星期几数字的映射表如下

| 星期几 | 数字 |
| ------ | ---- |
| 星期一 | 0    |
| 星期二 | 1    |
| 星期三 | 2    |
| 星期四 | 3    |
| 星期五 | 4    |
| 星期六 | 5    |
| 星期日 | 6    |

下面是默认节日“元旦”和“母亲节”的格式

```json
{
  "name": "元旦",
  "type": "Solar",
  "date": [
    1,
    1
  ],
  "message": [
    "岁月如歌蝶恋花，新年朝阳艳如画。元旦喜庆福相随，天地共舞春又归。白雪纷飞送福至，红霞满天寄心意。真诚话语不多说，敬祝佳节多快乐。",
    "新年新开端，首选是元旦。立志好人缘，天天露笑脸。健康常相伴，饮食加锻炼。好运在蛇年，快乐过元旦。祝：元旦快乐！"
  ]
}
```

```json
{
  "name": "母亲节",
  "type": "Week",
  "date": [
    5,
    2,
    6
  ],
  "message": [
    "世上只有妈妈好，投入妈妈怀抱，困难也能看作宝，勤奋努力步步高，如意幸福都来到，祝天下母亲节日快乐，身体健康，平安吉祥!",
    "让我们多给母亲一点爱与关怀，那怕是酷暑中的一把扇子;寒冬中的一件毛衣，让母亲时刻感受儿女的关心，母亲节快乐!"
  ]
}
```

在[wish_message/message.py](./wish_message/message.py)中的函数`check_legitimacy`可以为你检查节日中的错误，你可以使用如下代码来检查你的节日

```python
from json import load

from wish_message.message import check_legitimacy

with open("config/wish_message/wish_days.json", "r", encoding="utf8") as f:  # 替换为自己节日文件位置
    check_legitimacy(load(f))
```

