# 03-通过API生成文本

## 开篇除恐

上一章我们明白了LLM是什么，但还有一个问题：**我怎么用它？**

是不是要自己买一堆服务器？要懂深度学习？要写几百行代码？

完全不用。

调AI的API，就像**点外卖**。你不需要知道厨师怎么做菜，你只需要：
1. 打开外卖APP（API）
2. 选好菜品（prompt）
3. 下单（发送请求）
4. 等快递（收到响应）

这一章教你"点外卖"。

---

## 白话化：把术语扒光了看

### API

**大白话**：API就是** waiter **（服务员）。你跟他说"来份宫保鸡丁"，他传给厨房，厨房做好后端给你。

你不需要进厨房，不需要会做饭，只需要**会说话**（写prompt）。

### Completion API

**大白话**：Completion API是"续写模式"。你给它前半句，它续写后半句。

**原书说明**：Completion API是OpenAI最早提供的接口，适用于非对话场景的文本生成。

### Chat Completion API

**大白话**：Chat Completion API是"对话模式"。你扮演用户，它扮演助手，来回聊天。

**原书说明**：Chat Completion API支持多轮对话，通过`messages`数组传递上下文。

### Streaming（流式输出）

**大白话**：Streaming就是**边做边传**。不是等整篇文章写完再给你，而是一个词一个词地吐出来，像打字机效果。

**好处**：用户体验更好，不用干等。

### Temperature（温度）

**大白话**：Temperature控制AI的" creativity "（创造力）。

- Temperature = 0：AI变得** deterministic **，同样的输入永远同样的输出。适合需要准确答案的场景（如客服）。
- Temperature = 1：AI变得** creative **，同样的输入可能给出不同回答。适合需要创意的场景（如写诗、写广告）。
- Temperature = 2：AI变得** wild **，回答可能完全不着边际。

**原书说明**：Temperature范围0-2，默认1。越高越随机。

### Top_p

**大白话**：Top_p也是控制随机性的，和Temperature类似，但思路不同。

- Top_p = 1：AI从所有可能的词里选。
- Top_p = 0.1：AI只从最可能的10%的词里选。

**原书说明**：Top_p是nucleus sampling，通常建议改Temperature或Top_p其中之一，不要同时改。

### Token限制

**大白话**：token限制就是AI的"话费"。你用的token越多，花钱越多。

**原书说明**：API按token计费，输入和输出都算。需要合理控制max_tokens。

---

## 直觉先行：用HTTP请求类比API调用

API调用本质上就是一个**HTTP POST请求**：

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
  }'
```

这和你网上填表单、提交数据没有任何本质区别。

**Python版本**（更常用）：

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
)

print(response.choices[0].message.content)
```

就这？**对，就这。**

---

## 例子贴身

### ☼ 热身：用curl调用OpenAI API

**自编** 打开终端，输入：

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "用一句话解释什么是API"}
    ]
  }'
```

你会得到类似这样的JSON响应：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "API是应用程序之间通信的接口..."
      }
    }
  ]
}
```

这就是AI的回复，藏在`choices[0].message.content`里。

### ☼☼ 正经：给客服机器人实现基础问答（贯穿例子·第3章）

**场景**：第2章你选了GPT-3.5 Turbo，现在要让它真正回答客服问题。

**原书** 展示了Azure OpenAI和OpenAI API的基本调用方式，包括环境变量配置、模型调用、参数设置。

**自编** 你写了第一个客服机器人：

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def customer_service_qa(question):
    """客服问答函数"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.3,  # 客服需要准确，不要creativity
        messages=[
            {"role": "system", "content": "你是XX电商的客服代表，回答要简洁、礼貌、准确。"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

# 测试
print(customer_service_qa("我的订单什么时候到？"))
```

**输出示例**：

> "您好！您的订单预计3-5个工作日送达。如需查询具体物流信息，请提供订单号，我将为您查询最新状态。"

**原书** 提到，可以用Azure content safety filter过滤不当内容。如果触发内容过滤，API会返回`finish_reason: "content_filter"`。

**你的第一个完整Demo诞生了**。虽然它还只能泛泛而谈，但已经能工作。

---

## 这一章要带走的东西

- API就是" waiter "，你不需要懂后端，只需要会写prompt。
- Completion API用于续写，Chat Completion API用于对话。
- Streaming让AI"边想边说"，体验更好。
- Temperature控制随机性：0= deterministic ，1= creative 。
- Top_p也是控制随机性，和Temperature二选一。
- 按token计费，要控制输入输出长度。
- Azure content safety filter会自动过滤不当内容。
- 我们的客服机器人有了第一个可工作的Demo。

**就这样。**
## API鍩虹娣卞害瑙ｆ瀽

### API鐨勬湰璐?
**澶х櫧璇?*锛欰PI锛圓pplication Programming Interface锛夊氨鏄湇鍔″憳銆備綘璺熶粬璇存潵浠藉淇濋浮涓侊紝浠栦紶缁欏帹鎴匡紝鍘ㄦ埧鍋氬ソ鍚庣缁欎綘銆?
浣犱笉闇€瑕佽繘鍘ㄦ埧锛屼笉闇€瑕佷細鍋氶キ锛屽彧闇€瑕佷細璇磋瘽锛堝啓prompt锛夈€?
**鎶€鏈畾涔?*锛欰PI鏄竴缁勯鍏堝畾涔夊ソ鐨勫嚱鏁板拰鍗忚锛屽厑璁稿簲鐢ㄧ▼搴忎箣闂寸浉浜掗€氫俊銆傚湪LLM鍦烘櫙涓紝API璁╀綘鍙互閫氳繃缃戠粶璋冪敤澶фā鍨嬬殑鑳藉姏銆?
### RESTful API

**姒傚康**锛歊EST锛圧epresentational State Transfer锛夋槸涓€绉嶈蒋浠舵灦鏋勯鏍硷紝寰堝鐜颁唬API閮介伒寰猂EST鍘熷垯銆?
**鏍稿績鐗圭偣**锛?- **鏃犵姸鎬?*锛氭瘡娆¤姹傞兘鍖呭惈鎵€鏈夊繀瑕佷俊鎭?- **璧勬簮瀵煎悜**锛氭瘡涓猆RL浠ｈ〃涓€涓祫婧?- **HTTP鏂规硶**锛欸ET锛堟煡璇級銆丳OST锛堝垱寤猴級銆丳UT锛堟洿鏂帮級銆丏ELETE锛堝垹闄わ級

**LLM API鐨凴ESTful璁捐**锛?- POST /v1/chat/completions - 鍒涘缓瀵硅瘽瀹屾垚
- POST /v1/completions - 鍒涘缓鏂囨湰瀹屾垚
- GET /v1/models - 鑾峰彇鍙敤妯″瀷鍒楄〃
- GET /v1/usage - 鑾峰彇浣跨敤缁熻

### 涓轰粈涔堢敤API鑰屼笉鏄湰鍦伴儴缃诧紵

**API鐨勪紭鍔?*锛?1. **闆跺熀纭€璁炬柦**锛氫笉闇€瑕佷拱GPU鏈嶅姟鍣?2. **鑷姩鏇存柊**锛氳嚜鍔ㄨ幏寰楁渶鏂版ā鍨?3. **寮规€т几缂?*锛氳嚜鍔ㄥ鐞嗗嘲鍊兼祦閲?4. **涓撲笟缁存姢**锛氫緵搴斿晢璐熻矗杩愮淮

**API鐨勫姡鍔?*锛?1. **鎸佺画鎴愭湰**锛氭寜浣跨敤閲忎粯璐癸紝闀挎湡鍙兘璐?2. **鏁版嵁闅愮**锛氭暟鎹渶瑕佷紶鍒颁簯绔?3. **渚濊禆渚涘簲鍟?*锛氫緵搴斿晢娑ㄤ环銆佹湇鍔′腑鏂細褰卞搷浣?4. **瀹氬埗鍖栭檺鍒?*锛氭棤娉曚慨鏀规ā鍨嬪唴閮?
---

## 涓绘祦API鎻愪緵鍟嗗姣?
### OpenAI

**妯″瀷**锛?- GPT-4锛氭渶寮猴紝澶氭ā鎬侊紝閫傚悎澶嶆潅浠诲姟
- GPT-4 Turbo锛氭洿蹇洿渚垮疁锛?28K涓婁笅鏂?- GPT-3.5 Turbo锛氭€т环姣斾箣鐜?- DALL-E 3锛氬浘鍍忕敓鎴?
**鐗圭偣**锛?- 妯″瀷鑳藉姏涓氱晫棰嗗厛
- API绋冲畾鍙潬
- 鏂囨。涓板瘜锛岀ぞ鍖烘椿璺?- 浠锋牸杈冮珮

**浠锋牸锛堝弬鑰冿級**锛?- GPT-4锛?30/1M input tokens, $60/1M output tokens
- GPT-3.5 Turbo锛?0.50/1M input tokens, $1.50/1M output tokens

**閫傜敤鍦烘櫙**锛?- 杩芥眰鏈€寮鸿兘鍔?- 棰勭畻鍏呰冻
- 闇€瑕佹渶鏂版妧鏈?
---

### Anthropic

**妯″瀷**锛?- Claude 3 Opus锛氭渶寮猴紝鎺ㄧ悊鑳藉姏寮?- Claude 3 Sonnet锛氬潎琛★紝鎬т环姣旈珮
- Claude 3 Haiku锛氬揩閫熶究瀹?
**鐗圭偣**锛?- 瓒呴暱涓婁笅鏂囷紙200K tokens锛?- 寮哄畨鍏ㄦ€?- 鎿呴暱闀挎枃妗ｅ鐞?- 涓枃鑳藉姏涓嶉敊

**浠锋牸锛堝弬鑰冿級**锛?- Claude 3 Opus锛?15/1M input tokens, $75/1M output tokens
- Claude 3 Sonnet锛?3/1M input tokens, $15/1M output tokens

**閫傜敤鍦烘櫙**锛?- 闀挎枃妗ｅ垎鏋?- 闇€瑕佸己瀹夊叏鎬?- 澶嶆潅鎺ㄧ悊浠诲姟

---

### Google

**妯″瀷**锛?- Gemini Ultra锛氭渶寮猴紝澶氭ā鎬?- Gemini Pro锛氭€т环姣旈珮
- Gemini Nano锛氱渚ч儴缃?
**鐗圭偣**锛?- 鍘熺敓澶氭ā鎬?- 瓒呴暱涓婁笅鏂囷紙100涓噒oken锛孏emini 1.5 Pro锛?- 涓嶨oogle鐢熸€侀泦鎴?- 浠锋牸鏈夌珵浜夊姏

**浠锋牸锛堝弬鑰冿級**锛?- Gemini Pro锛?0.50/1M input tokens, $1.50/1M output tokens

**閫傜敤鍦烘櫙**锛?- 澶氭ā鎬佸簲鐢?- 闀挎枃妗ｅ鐞?- 宸茬粡浣跨敤Google浜?
---

### 鍥藉唴鎻愪緵鍟?
**鐧惧害鏂囧績涓€瑷€**锛?- 妯″瀷锛欵RNIE Bot
- 鐗圭偣锛氫腑鏂囩悊瑙ｅ己锛岀粨鍚堢櫨搴︽悳绱?- 浠锋牸锛氳緝浣?- 閫傜敤锛氫腑鏂囧満鏅€佸浗鍐呴儴缃?
**闃块噷閫氫箟鍗冮棶**锛?- 妯″瀷锛歈wen
- 鐗圭偣锛氬妯℃€侊紝寮€婧怮wen绯诲垪
- 浠锋牸锛氳緝浣?- 閫傜敤锛氫紒涓氬簲鐢ㄣ€佷腑鏂囧満鏅?
**鑵捐娣峰厓**锛?- 妯″瀷锛欻unyuan
- 鐗圭偣锛氫笌寰俊鐢熸€侀泦鎴?- 閫傜敤锛氬井淇＄敓鎬佸簲鐢?
**鏅鸿氨ChatGLM**锛?- 妯″瀷锛欳hatGLM
- 鐗圭偣锛氫腑鑻卞弻璇紝闀夸笂涓嬫枃锛屽紑婧?- 閫傜敤锛氬紑鍙戣€呭拰浼佷笟

**浠锋牸**锛氬浗鍐呮ā鍨嬩环鏍兼櫘閬嶈緝浣庯紝绾?.004-0.012鍏?1K tokens銆?
---

### 寮€婧愭ā鍨婣PI

**Hugging Face Inference API**锛?- 鏀寔鏁板崈涓紑婧愭ā鍨?- 鎸夐渶浠樿垂
- 鍏嶈垂棰濆害锛氶€傚悎娴嬭瘯

**Together AI**锛?- 鎻愪緵寮€婧愭ā鍨婣PI
- 浠锋牸浣?- 鏀寔蹇€熷疄楠?
**Groq**锛?- 瓒呭揩鎺ㄧ悊閫熷害
- 閫傚悎浣庡欢杩熷満鏅?
---

## API璁よ瘉鍜屽畨鍏?
### API瀵嗛挜绠＄悊

**浠€涔堟槸API瀵嗛挜**锛?- API瀵嗛挜鏄皟鐢ˋPI鐨勮韩浠借瘉
- 閫氬父鏄竴涓查暱瀛楃涓?- 鐢ㄤ簬韬唤楠岃瘉鍜岃璐?
**瀹夊叏瀛樺偍**锛?```python
# 閿欒锛氱‖缂栫爜鍦ㄤ唬鐮侀噷
api_key = "sk-xxxxxxxxxxxx"

# 姝ｇ‘锛氫娇鐢ㄧ幆澧冨彉閲?import os
api_key = os.environ["OPENAI_API_KEY"]

# 姝ｇ‘锛氫粠閰嶇疆鏂囦欢璇诲彇锛堥厤缃枃浠朵笉鎻愪氦鍒癎it锛?import dotenv
dotenv.load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]
```

**鏈€浣冲疄璺?*锛?- 姘歌繙涓嶈纭紪鐮丄PI瀵嗛挜
- 浣跨敤鐜鍙橀噺鎴栧瘑閽ョ鐞嗘湇鍔?- 瀹氭湡杞崲瀵嗛挜
- 涓嶅悓鐜浣跨敤涓嶅悓瀵嗛挜锛堝紑鍙戙€佹祴璇曘€佺敓浜э級

---

### 閫熺巼闄愬埗锛圧ate Limit锛?
**浠€涔堟槸閫熺巼闄愬埗**锛?- API渚涘簲鍟嗛檺鍒跺崟浣嶆椂闂村唴鐨勮姹傛鏁?- 闃叉婊ョ敤鍜屼繚璇佹湇鍔¤川閲?
**甯歌鐨勯檺娴佺瓥鐣?*锛?- **RPM锛圧equests Per Minute锛?*锛氭瘡鍒嗛挓璇锋眰鏁?- **TPM锛圱okens Per Minute锛?*锛氭瘡鍒嗛挓Token鏁?- **RPD锛圧equests Per Day锛?*锛氭瘡澶╄姹傛暟

**绀轰緥锛圤penAI GPT-4锛?*锛?- RPM锛?00
- TPM锛?50,000

**澶勭悊闄愭祦**锛?1. **鎸囨暟閫€閬?*锛氶亣鍒?29閿欒锛岀瓑寰?绉掋€?绉掋€?绉掋€?绉?..
2. **闄愭祦鍣?*锛氬湪浠ｇ爜涓疄鐜颁护鐗屾《鎴栨紡妗剁畻娉?3. **闃熷垪**锛氱敤闃熷垪缂撳啿璇锋眰锛屽钩婊戝彂閫?
**Python绀轰緥锛堟寚鏁伴€€閬匡級**锛?```python
import time
from openai import OpenAI, RateLimitError

client = OpenAI()

def call_with_retry(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4, 8, 16绉?                time.sleep(wait_time)
            else:
                raise
```

---

## 璇锋眰鍜屽搷搴旇瑙?
### 瀹屾暣鐨勮姹傜粨鏋?
```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="gpt-4",                          # 妯″瀷閫夋嫨
    messages=[                              # 瀵硅瘽鍘嗗彶
        {"role": "system", "content": "浣犳槸瀹㈡湇鍔╂墜锛屽洖绛旂敤鎴烽棶棰樸€?},
        {"role": "user", "content": "鎴戠殑璁㈠崟浠€涔堟椂鍊欏彂璐э紵"}
    ],
    temperature=0.3,                        # 闅忔満鎬ф帶鍒?    max_tokens=500,                         # 鏈€澶ц緭鍑洪暱搴?    top_p=1.0,                              # nucleus閲囨牱
    frequency_penalty=0.0,                  # 棰戠巼鎯╃綒
    presence_penalty=0.0,                   # 瀛樺湪鎯╃綒
    stop=None,                              # 鍋滄鏍囪
    stream=False                            # 鏄惁娴佸紡杈撳嚭
)
```

**鍙傛暟璇﹁В**锛?
| 鍙傛暟 | 绫诲瀷 | 榛樿鍊?| 璇存槑 |
|------|------|--------|------|
| model | string | - | 妯″瀷鍚嶇О |
| messages | array | - | 瀵硅瘽娑堟伅鏁扮粍 |
| temperature | float | 1 | 0-2锛屾帶鍒堕殢鏈烘€?|
| max_tokens | int | 鏃犵┓ | 鏈€澶ц緭鍑簍oken鏁?|
| top_p | float | 1 | 0-1锛宯ucleus閲囨牱 |
| frequency_penalty | float | 0 | -2鍒?锛屾儵缃氶噸澶嶈瘝 |
| presence_penalty | float | 0 | -2鍒?锛屾儵缃氬凡鍑虹幇璇?|
| stop | string/array | None | 鍋滄鐢熸垚鐨勬爣璁?|
| stream | boolean | False | 鏄惁娴佸紡杈撳嚭 |

---

### 瀹屾暣鐨勫搷搴旂粨鏋?
```python
response = client.chat.completions.create(...)

# 璁块棶鍝嶅簲鍐呭
content = response.choices[0].message.content
role = response.choices[0].message.role
finish_reason = response.choices[0].finish_reason

# 璁块棶鐢ㄩ噺淇℃伅
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

# 璁块棶妯″瀷淇℃伅
model = response.model
id = response.id
created = response.created
```

**鍝嶅簲瀛楁璇﹁В**锛?
| 瀛楁 | 璇存槑 |
|------|------|
| id | 鏈璇锋眰鐨勫敮涓€ID |
| object | 瀵硅薄绫诲瀷锛坈hat.completion锛?|
| created | 鍒涘缓鏃堕棿锛圲nix鏃堕棿鎴筹級 |
| model | 浣跨敤鐨勬ā鍨?|
| choices | 鐢熸垚鐨勫洖绛斿垪琛?|
| choices[0].message | 鐢熸垚鐨勬秷鎭?|
| choices[0].finish_reason | 鐢熸垚缁撴潫鍘熷洜 |
| usage | Token浣跨敤缁熻 |
| usage.prompt_tokens | 杈撳叆Token鏁?|
| usage.completion_tokens | 杈撳嚭Token鏁?|
| usage.total_tokens | 鎬籘oken鏁?|

---

## 澶氳疆瀵硅瘽绠＄悊

### 瀵硅瘽涓婁笅鏂?
**鍘熺悊**锛歀LM鏈韩鏃犵姸鎬侊紝姣忔璋冪敤閮介渶瑕佷紶閫掑畬鏁村璇濆巻鍙层€?
**绀轰緥**锛?```python
# 瀵硅瘽鍘嗗彶
messages = [
    {"role": "system", "content": "浣犳槸瀹㈡湇鍔╂墜銆?},
    {"role": "user", "content": "鎴戠殑璁㈠崟浠€涔堟椂鍊欏彂璐э紵"},
    {"role": "assistant", "content": "璇锋彁渚涙偍鐨勮鍗曞彿锛屾垜甯偍鏌ヨ銆?},
    {"role": "user", "content": "璁㈠崟鍙锋槸12345銆?}
]

# 鍙戦€佸寘鍚畬鏁村巻鍙茬殑璇锋眰
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages
)
```

### 涓婁笅鏂囩獥鍙ｇ鐞?
**闂**锛氫笂涓嬫枃绐楀彛鏈夐檺锛堝16K tokens锛夛紝闀垮璇濅細瓒呭嚭銆?
**瑙ｅ喅鏂规**锛?
**1. 婊戝姩绐楀彛**锛?- 鍙繚鐣欐渶杩慛杞璇?- 鏃╂湡瀵硅瘽琚涪寮?
**2. 鎽樿鍘嬬缉**锛?- 瀹氭湡鎶婃棭鏈熷璇濇€荤粨鎴愭憳瑕?- 鎶婃憳瑕佹斁鍏ヤ笂涓嬫枃

**3. RAG**锛?- 鎶婂璇濆巻鍙插瓨鍏ュ悜閲忔暟鎹簱
- 闇€瑕佹椂妫€绱㈢浉鍏冲巻鍙?
**Python绀轰緥锛堟粦鍔ㄧ獥鍙ｏ級**锛?```python
MAX_HISTORY = 10  # 鏈€澶氫繚鐣?0杞璇?
def add_message(history, role, content):
    history.append({"role": role, "content": content})
    # 淇濈暀system娑堟伅 + 鏈€杩慚AX_HISTORY杞?    if len(history) > MAX_HISTORY + 1:
        # 淇濈暀绗竴鏉ystem娑堟伅
        system = history[0]
        # 淇濈暀鏈€杩慚AX_HISTORY杞?        recent = history[-MAX_HISTORY:]
        history = [system] + recent
    return history
```

---

## 娴佸紡杈撳嚭锛圫treaming锛?
### 浠€涔堟槸娴佸紡杈撳嚭锛?
**澶х櫧璇?*锛氫笉鏄瓑鏁寸瘒鏂囩珷鍐欏畬鍐嶇粰浣狅紝鑰屾槸涓€涓瘝涓€涓瘝鍦板悙鍑烘潵锛屽儚鎵撳瓧鏈烘晥鏋溿€?
**濂藉**锛?- 鐢ㄦ埛浣撻獙鏇村ソ锛屼笉鐢ㄥ共绛?- 鍙互瀹炴椂鐪嬪埌鐢熸垚杩囩▼
- 閫傚悎闀挎枃鏈敓鎴?
### 瀹炵幇娴佸紡杈撳嚭

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "璇峰啓涓€棣栧叧浜庢槬澶╃殑璇椼€?}
    ],
    stream=True  # 寮€鍚祦寮忚緭鍑?)

# 閫愪釜chunk澶勭悊
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

**杈撳嚭鏁堟灉**锛?```
鏄ラ鍚规媯澶у湴锛?涓囩墿澶嶈嫃鐢熸満銆?鑺卞紑婊″洯棣欐孩锛?楦熼福鏋濆ご娆㈡瓕銆?```

### 娴佸紡杈撳嚭鐨勫簲鐢ㄥ満鏅?
**1. 鑱婂ぉ鏈哄櫒浜?*锛?- 瀹炴椂鏄剧ずAI鍥炲
- 鐢ㄦ埛鎰熻鍝嶅簲鏇村揩

**2. 闀挎枃鏈敓鎴?*锛?- 鎶ュ憡銆佹枃绔犮€佷唬鐮?- 鐢ㄦ埛鍙互鎻愬墠鐪嬪埌鍐呭

**3. 瀹炴椂缈昏瘧**锛?- 杈瑰惉杈圭炕璇?- 浣庡欢杩熶綋楠?
---

## 鍑芥暟璋冪敤锛團unction Calling锛?
### 浠€涔堟槸鍑芥暟璋冪敤锛?
**澶х櫧璇?*锛欰I涓嶄粎鑳借亰澶╋紝杩樿兘璋冪敤宸ュ叿銆備綘闂寳浜ぉ姘旀€庝箞鏍凤紝AI鍙互璋冪敤澶╂皵API鏌ヨ锛岀劧鍚庢妸缁撴灉鍛婅瘔浣犮€?
### 濡備綍瀹炵幇锛?
**姝ラ1锛氬畾涔夊伐鍏?*
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "鏌ヨ鎸囧畾鍩庡競鐨勫ぉ姘?,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "鍩庡競鍚嶇О锛屽鍖椾含銆佷笂娴?
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "娓╁害鍗曚綅"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

**姝ラ2锛氬彂閫佽姹?*
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "鍖椾含浠婂ぉ澶╂皵鎬庝箞鏍凤紵"}
    ],
    tools=tools
)
```

**姝ラ3锛氬鐞嗗嚱鏁拌皟鐢?*
```python
# AI鍐冲畾璋冪敤get_weather鍑芥暟
function_call = response.choices[0].message.tool_calls[0]
function_name = function_call.function.name
arguments = json.loads(function_call.function.arguments)

# 鎵ц鍑芥暟
if function_name == "get_weather":
    result = get_weather(arguments["city"], arguments.get("unit", "celsius"))

# 鎶婄粨鏋滆繑鍥炵粰AI
second_response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "鍖椾含浠婂ぉ澶╂皵鎬庝箞鏍凤紵"},
        response.choices[0].message,  # AI鐨勫嚱鏁拌皟鐢ㄨ姹?        {
            "role": "tool",
            "tool_call_id": function_call.id,
            "content": json.dumps(result)
        }
    ]
)
```

### 鍑芥暟璋冪敤鐨勫簲鐢?
**1. 澶栭儴API闆嗘垚**锛?- 鏌ヨ澶╂皵銆佽偂绁ㄣ€佽埅鐝?- 鎿嶄綔鏁版嵁搴?- 璋冪敤浼佷笟鍐呴儴绯荤粺

**2. 宸ュ叿浣跨敤**锛?- 璁＄畻鍣?- 鎼滅储寮曟搸
- 浠ｇ爜鎵ц鍣?
**3. 澶嶆潅宸ヤ綔娴?*锛?- 澶氭楠や换鍔?- 鏉′欢鍒ゆ柇
- 鏁版嵁鑱氬悎

---

## API璋冪敤鐨勬渶浣冲疄璺?
### 1. 鎻愮ず璇嶅伐绋?
**绯荤粺鎻愮ず璇嶏紙System Prompt锛?*锛?```python
messages = [
    {
        "role": "system",
        "content": "浣犳槸XX鍏徃鐨勫鏈嶄唬琛紝鍚嶅彨灏忓姪鎵嬨€傝鐢ㄥ弸濂姐€佷笓涓氱殑璇皵鍥炵瓟鐢ㄦ埛闂銆傚鏋滀笉鐭ラ亾绛旀锛岃璇氬疄鍦拌涓嶇煡閬擄紝涓嶈缂栭€犮€?
    },
    {"role": "user", "content": "..."}
]
```

**浣滅敤**锛?- 璁惧畾AI鐨勮鑹插拰琛屼负
- 鎻愪緵鑳屾櫙淇℃伅
- 寤虹珛鍥炵瓟椋庢牸

### 2. 鎻愮ず璇嶆ā鏉垮寲

**涓轰粈涔?*锛氫繚璇佷竴鑷存€э紝渚夸簬缁存姢銆?
**绀轰緥**锛?```python
SYSTEM_PROMPT_TEMPLATE = "浣犳槸{company}鐨勫鏈嶄唬琛紝鍚嶅彨{name}銆傝姘旓細{tone}銆傜煡璇嗛鍩燂細{domain}銆傚鏋滀笉鐭ラ亾绛旀锛岃璇存垜闇€瑕佹煡璇竴涓嬶紝璇风◢绛夈€?

def get_system_prompt(company, name, tone, domain):
    return SYSTEM_PROMPT_TEMPLATE.format(
        company=company,
        name=name,
        tone=tone,
        domain=domain
    )
```

### 3. 杈撳嚭缁撴瀯鍖?
**涓轰粈涔?*锛氭柟渚跨▼搴忚В鏋愬拰澶勭悊銆?
**鏂规硶**锛氬湪prompt涓姹侫I杈撳嚭鐗瑰畾鏍煎紡銆?
```python
prompt = "璇峰垎鏋愪互涓嬬敤鎴峰弽棣堢殑鎯呮劅鍊惧悜銆傜敤鎴峰弽棣堬細{feedback}銆傝浠SON鏍煎紡鍥炵瓟锛歿\"sentiment\": \"positive/neutral/negative\", \"confidence\": 0.0-1.0, \"reason\": \"绠€鐭鏄嶾"}"

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

result = json.loads(response.choices[0].message.content)
```

### 4. 鎴愭湰鎺у埗

**绛栫暐**锛?1. **閫夋嫨鍚堥€傜殑妯″瀷**锛氱畝鍗曚换鍔＄敤灏忔ā鍨?2. **鎺у埗max_tokens**锛氶檺鍒惰緭鍑洪暱搴?3. **鍘嬬缉prompt**锛氬噺灏戜笉蹇呰鐨則oken
4. **缂撳瓨缁撴灉**锛氱浉鍚岄棶棰樹笉閲嶅璋冪敤
5. **鎵归噺澶勭悊**锛氬涓姹傚悎骞?
### 5. 鐩戞帶鍜屾棩蹇?
**璁板綍浠€涔?*锛?- Prompt鍜屽搷搴斿唴瀹?- Token浣跨敤閲?- 鍝嶅簲鏃堕棿
- 閿欒淇℃伅
- 鐢ㄦ埛鍙嶉

**鐢ㄩ€?*锛?- 闂鎺掓煡
- 鏁堟灉鍒嗘瀽
- 鎴愭湰鎺у埗
- 鎸佺画浼樺寲

---

## 甯歌闂鍜岃В鍐虫柟妗?
### 闂1锛氬搷搴斿お鎱?
**鍘熷洜**锛?- 妯″瀷鎺ㄧ悊鎱紙GPT-4姣擥PT-3.5鎱級
- 涓婁笅鏂囧お闀?- 缃戠粶寤惰繜
- API闄愭祦

**瑙ｅ喅鏂规**锛?1. 鍒囨崲鍒版洿蹇殑妯″瀷
2. 缂╃煭prompt鍜屼笂涓嬫枃
3. 浣跨敤娴佸紡杈撳嚭
4. 瀹炵幇缂撳瓨
5. 閫夋嫨鏇磋繎鐨凙PI鍖哄煙

### 闂2锛氱粨鏋滀笉鍑嗙‘

**鍘熷洜**锛?- Prompt涓嶆竻鏅?- 妯″瀷鑳藉姏涓嶈冻
- 缂轰箯涓婁笅鏂?
**瑙ｅ喅鏂规**锛?1. 浼樺寲prompt
2. 鎻愪緵鏇村涓婁笅鏂?3. 浣跨敤RAG
4. 鍒囨崲鍒版洿寮虹殑妯″瀷
5. 娣诲姞楠岃瘉姝ラ

### 闂3锛氭垚鏈秴鏀?
**鍘熷洜**锛?- 璋冪敤浜嗗お澶氭API
- 浣跨敤浜嗗お璐电殑妯″瀷
- prompt澶暱
- 娌℃湁缂撳瓨

**瑙ｅ喅鏂规**锛?1. 瀹炴柦缂撳瓨绛栫暐
2. 浼樺寲prompt闀垮害
3. 閫夋嫨鍚堥€傜殑妯″瀷
4. 璁剧疆棰勭畻鍛婅
5. 鎵归噺澶勭悊

### 闂4锛氬唴瀹硅鎷︽埅

**鍘熷洜**锛?- Prompt鎴栬緭鍑哄寘鍚晱鎰熷唴瀹?- 骞冲彴鍐呭鏀跨瓥鍙樺寲

**瑙ｅ喅鏂规**锛?1. 璋冩暣prompt鎺緸
2. 鏄庣‘浣跨敤鍦烘櫙
3. 鑱旂郴骞冲彴瀹㈡湇
4. 鑰冭檻鑷墭绠℃ā鍨?
---

## 瀹炴垬妗堜緥锛氭瀯寤哄鏈岮PI璋冪敤

### 闇€姹?- 鎺ユ敹鐢ㄦ埛闂
- 鏌ヨ鐭ヨ瘑搴?- 鐢熸垚鍥炵瓟
- 杩斿洖JSON鏍煎紡

### 浠ｇ爜瀹炵幇
```python
from openai import OpenAI
import json

client = OpenAI(api_key="YOUR_API_KEY")

SYSTEM_PROMPT = "浣犳槸鐢靛晢瀹㈡湇鍔╂墜銆傝鏍规嵁鎻愪緵鐨勭煡璇嗗簱鍥炵瓟鐢ㄦ埛闂銆傚鏋滅煡璇嗗簱涓病鏈夌瓟妗堬紝璇疯鎴戦渶瑕佹煡璇竴涓嬶紝璇风◢绛夈€傝姘旓細鍙嬪ソ銆佷笓涓氥€傝緭鍑烘牸寮忥細JSON"

KNOWLEDGE_BASE = '''
閫€璐ф斂绛栵細7澶╂棤鐞嗙敱閫€璐э紝闇€瑕佷繚鎸佸晢鍝佸畬濂姐€?鍙戣揣鏃堕棿锛氫笅鍗曞悗24灏忔椂鍐呭彂璐э紝涓€鑸?-5澶╁埌璐с€?鐗╂祦鏌ヨ锛氳鎻愪緵璁㈠崟鍙锋煡璇㈢墿娴佺姸鎬併€?'''

def customer_service(user_question):
    prompt = f"鐭ヨ瘑搴擄細\n{KNOWLEDGE_BASE}\n\n鐢ㄦ埛闂锛歿user_question}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    return result

# 娴嬭瘯
result = customer_service("鎴戠殑璁㈠崟浠€涔堟椂鍊欏彂璐э紵")
print(result)
```

### 杈撳嚭绀轰緥
```json
{
    "answer": "鏍规嵁鎴戜滑鐨勫彂璐ф斂绛栵紝涓嬪崟鍚?4灏忔椂鍐呭彂璐э紝涓€鑸?-5澶╁彲浠ュ埌璐с€傚鏋滄偍闇€瑕佹煡璇㈠叿浣撹鍗曠殑鐗╂祦鐘舵€侊紝璇锋彁渚涜鍗曞彿銆?,
    "confidence": 0.9,
    "need_human": false
}
```

---

## API鐗堟湰绠＄悊

### 涓轰粈涔堥渶瑕佺増鏈鐞嗭紵

API浼氫笉鏂洿鏂帮細
- 鏂板姛鑳?- Bug淇
- 鍙傛暟鍙樺寲
- 妯″瀷鍗囩骇

### 鐗堟湰绠＄悊绛栫暐

**1. 鍥哄畾鐗堟湰**锛?```python
# 鎸囧畾鍏蜂綋鐗堟湰锛岄伩鍏嶈嚜鍔ㄦ洿鏂板鑷寸殑闂
response = client.chat.completions.create(
    model="gpt-4-0314",  # 2024骞?鏈?4鏃ョ殑鐗堟湰
    ...
)
```

**2. 鍒悕浣跨敤**锛?```python
# 浣跨敤鍒悕锛岃嚜鍔ㄦ寚鍚戞渶鏂扮ǔ瀹氱増鏈?response = client.chat.completions.create(
    model="gpt-4-turbo",  # 鑷姩鎸囧悜鏈€鏂扮殑turbo鐗堟湰
    ...
)
```

**3. 鍏煎鎬ф祴璇?*锛?- 鏂扮増鏈彂甯冨墠娴嬭瘯
- 鐏板害鍙戝竷
- 淇濈暀鍥炴粴鑳藉姏

---

## 鎴愭湰鐩戞帶鍜屼紭鍖?
### 鎴愭湰鏋勬垚

**涓昏鎴愭湰**锛?1. **API璋冪敤璐圭敤**锛氭寜token璁¤垂
2. **寮€鍙戞垚鏈?*锛氬紑鍙戝拰缁存姢浜哄姏
3. **鍩虹璁炬柦**锛氭湇鍔″櫒銆佹暟鎹簱绛?
### 鐩戞帶鎸囨爣

```python
# 璁板綍姣忔璋冪敤鐨勬垚鏈?def track_cost(prompt_tokens, completion_tokens, model):
    cost = calculate_cost(prompt_tokens, completion_tokens, model)
    log_to_monitoring({
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": cost,
        "timestamp": time.time()
    })
```

### 浼樺寲绛栫暐

**1. 妯″瀷閫夋嫨浼樺寲**锛?- 绠€鍗曚换鍔＄敤灏忔ā鍨?- 澶嶆潅浠诲姟鐢ㄥぇ妯″瀷

**2. Prompt浼樺寲**锛?- 鍑忓皯涓嶅繀瑕佺殑token
- 鍘嬬缉prompt

**3. 缂撳瓨绛栫暐**锛?- 鐑偣闂缂撳瓨
- 璇箟缂撳瓨

**4. 鎵归噺澶勭悊**锛?- 澶氫釜璇锋眰鍚堝苟

---

## 鏈珷鎬濊€冮

1. **API鍜屾湰鍦伴儴缃叉湁浠€涔堝尯鍒紵鍦ㄤ粈涔堟儏鍐典笅搴旇閫夋嫨鍝鏂规锛?*
   - 鍙傝€冿細鎴愭湰銆佹暟鎹畨鍏ㄣ€佸欢杩熴€佺淮鎶よ兘鍔?
2. **濡備綍璁捐涓€涓彲闈犵殑API璋冪敤绯荤粺锛熼渶瑕佽€冭檻鍝簺鏂归潰锛?*
   - 鍙傝€冿細閲嶈瘯鏈哄埗銆侀檺娴併€佺洃鎺с€侀檷绾?
3. **鍑芥暟璋冪敤锛團unction Calling锛夎В鍐充簡浠€涔堥棶棰橈紵涓句竴涓疄闄呭簲鐢ㄥ満鏅€?*
   - 鍙傝€冿細杩炴帴澶栭儴绯荤粺銆佹墽琛屽姩浣溿€佽幏鍙栧疄鏃舵暟鎹?
4. **濡備綍鎺у埗API璋冪敤鎴愭湰锛熷垪鍑鸿嚦灏?绉嶆柟娉曘€?*
   - 鍙傝€冿細妯″瀷閫夋嫨銆乸rompt浼樺寲銆佺紦瀛樸€佹壒閲忓鐞嗐€佺洃鎺?
5. **娴佸紡杈撳嚭鍜屾櫘閫氳緭鍑烘湁浠€涔堝尯鍒紵鍚勯€傜敤浜庝粈涔堝満鏅紵**
   - 鍙傝€冿細鐢ㄦ埛浣撻獙銆佸疄鏃舵€с€佸疄鐜板鏉傚害

---

**鏈珷鎵╁厖杩涜涓?..**

