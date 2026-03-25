# 個人開發規範

## 語言偏好
- 與 Claude 溝通一律使用繁體中文
- 程式碼註解使用繁體中文
- commit message 使用英文

## 架構風格
簡潔易懂，避免一坨屎山

### 目錄分層
```
utility/       # 核心模組，供執行入口主程式 import 使用
script/        # 一次性工具腳本（資料生成、轉換等經常改動測試的腳本）
configuration/ # 各 domain 或環境的設定檔（yaml）
.data/         # 資料集位置（向量資料庫、原始資料等等）
root/          # 執行入口（app.py、evaluate.py 等直接跑的 script）
```

### 原則
- 在 `utility/` 底下必須獨立不要相互引用
- 在 `root/` 底下的 python code 可以 import `utility/` 底下的模塊 
- 執行入口放專案根目錄
- 一次性工具放 `script/`，不污染根目錄
- 設定與程式碼分離

## 檔案命名慣例
- 禁止使用所有 `-` 以及 `_` 符號
- 禁止使用縮寫(包含id 以及 url 等習慣縮寫)
- 所有可見的檔案都需要用一個英文名詞單字來命名，除了 `__init__.py` 之外，需要嚴格遵守
  - 好的範例：
    - `application.py`
    - `configuration.yaml`
    - `environment`
  - 壞的範例：
    - `app.py`
    - `config.yaml`
    - `env`
- 在 `utility/` 底下的 python 模塊，前後都需要添加 `_` 來區別是模塊單位
  - 好的範例:
    - `utility/_vector_.py`
  - 壞的範例：
    - `utility/vector.py`
- 所有不可見的檔案前面都需要添加 `.` 來隱藏，命名方式不需要嚴格遵守

## 程式碼風格
風格是以 Explicit Termination 為核心，每個程式區塊都有明確的結束訊號
- 函式末尾明確 `return`，包含 `__init__` 的結尾也是
- 迴圈末尾明確 `continue`
- `class` 末尾明確 `pass`
- `return` 加括號

### 套件（Library）引用慣例
- 除了 `__init__.py` 以外，禁止使用 `from` 來引入模塊，確保變數名稱不會被覆蓋
  - 好的範例:
    - `import PIL.Image`
  - 壞的範例:
    - `from PIL import Image`
- `__init__.py` 作為套件入口，透過相對 `import` 暴露函式
  - 好的範例:
    `from ._vector_ import *`
  - 壞的範例
    `from utility._vector_ import *`

### 物件（Class）慣例
- 禁止使用所有的 `-` 以及 `_` 符號
- 所有物件都需要用一個英文名詞單字來命名，需要嚴格遵守
- 禁止使用縮寫(包含id 以及 url 等習慣縮寫)
- 除了 `__init__` 方法之外，所有物件中的方法需要嚴格遵守
  - 一個動詞搭配一個名詞方式來命名，順序不可變，也不可使用縮寫
    - 好的範例：
        - `getValue`
        - `openWindow`
        - `closeSession`
    - 壞的範例：
        - `get_value`
        - `Open_Window`
        - `closesession`
  - 動詞必須小寫，名詞第一個字母大寫
    - 好的範例：
        - `getValue`
        - `openWindow`
        - `closeSession`
    - 壞的範例：
        - `getvalue`
        - `OpenWindow`
        - `Closesession`
  - 只有 `get` 開頭的方法可以輸出任意物件，其他方法都是輸出 `True`
- 物件中的方法嚴格遵守函式的慣例

### 函式（Function）慣例
- 所有函數都嚴格遵守物件（Class）慣例
- 任意函數遵守強制型別標註，回傳值即使是 `None` 必須標註
  - 好的範例：
    - `getValue(apple: torch.Tensor) -> torch.Tensor:`
    - `openWindow(self) -> bool:`
    - `closeSession(self) -> bool:`
  - 壞的範例：
    - `getValue(apple):`
    - `getValue(apple: torch.Tensor):`
    - `openWindow(self):`

### 變數（Variable）慣例
所有變數都需要用一個英文名詞單字來命名，需要嚴格遵守，避免使用 `x1` 或 `x2` 等等
  - 禁止使用縮寫(包含id 以及 url 等習慣縮寫)
  - 要跟外部溝通，譬如資料庫或是其他API，在溝通前統一格式，譬如使用 dict 來封包
  - 如果有多個很類似的變數，或是當下必須被保留的，建議使用 dict 或 list 保存

## 開發哲學
- 先跑通，再優化
- 設定與邏輯分離（yaml config driven）
- 不同 domain 共用同一套 pipeline，差異只在 config
