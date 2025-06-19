<!-- 底下標籤來源參考寫法可至：https://github.com/Envoy-VC/awesome-badges#github-stats -->

# Drill Map AI 穴位圖異常分類模組

## 功能

讀取穴位圖進行正異常類型分類，對未知圖形則採用馬式距離方式推導對應模型後再進行分類  
**（穴位圖來源由CIM提供，需在公司內網執行，來源圖片僅保留最近3個月的資料）**

---

## 主要函式

### get_ai_classification

- **參數**
  - `product_name` (str): 要分類的圖號
  - `img_src` (str): 圖片的路徑

- **返回值**
  - 回傳一個 dictionary，包含以下 Key：
    - `classification_code` (str): 分類代碼 (TYPE0, TYPE1, TYPE3, TYPE4)，如果圖檔不存在則返回 'N/A'，如果超過距離範圍則返回 'UNKNOW'，如果無法分類則返回 'ERROR'和error message
    - `classification_model` (str): 使用的分類模型名稱
    - `distance` (float): 馬氏距離，如果已知圖號模型或無法計算則返回 -1

---

## 使用範例

```python
import drill_map_module as drill_ai
import asyncio

async def main():
    drill_map_ai = drill_ai.DrillMapAIModule()
    await drill_map_ai.async_init()  # 必須先做這一步初始化
    ai_return = await drill_map_ai.get_ai_classification(
        'A158200',
        'D:\\drill_map_backup\\ND35\\20230603030300ND35SP2L230524040Target.jpg'
    )
    print(ai_return)
    # 輸出例子: {'classification_code': 'TYPE3', 'classification_model': 'A158200_', 'distance': -1}

asyncio.run(main())
 
```

---

## 資料夾說明
- [example.py]()               # 引用模組範例程式
- [drill_map_module.py]()      # 穴位圖辨識主程式
- [test_drill_map_module.py]() # 單元測試[穴位圖辨識主程式]
- [requirements.txt]()         # 相依套件
- [README.md]()                # 專案說明文件
- [data_model/](#ai-辨識模型資料夾inference測試圖片-muti_classification-多分類辨識模型-two_classfication-二分類辨識模型) # AI 辨識模型資料夾

### AI 辨識模型資料夾(inference:測試圖片, muti_classification: 多分類辨識模型, two_classfication: 二分類辨識模型)
- data_model/                  
    ├── inference/             
    ├── multi_classification/  
    └── two_classification/    

---

## 專案技術
- Python 3.10.13
- PyQt5 5.15.10
- opencv-python 4.8.1.78
- cnocr 2.2.3.2
- scikit-learn 1.2.2
- albumentations 1.3.1
- autogluon 0.8.2
- torch 1.13.1
- torchvision 0.14.1
- icecream 2.1.4
- pandas 1.5.3
- numpy 1.26.4
- PIL 9.5.0

---

## 注意事項

- 請務必先執行 `await drill_map_ai.async_init()` 完成模型與統計資料初始化。
- 圖片路徑與產品型號需正確對應，否則可能回傳 `'N/A'` 或 `'ERROR'`。
- 若需自訂產品型號，請參考 `product_name_mapping` 於原始碼內的`_get_reference_config`裡擴充。

## uv使用
- 若要使用 uv 來啟動此模組，請確保已安裝 `uv` 並在終端機中執行以下命令：

### 確認目前安裝python版本 這裡指定3.10.13版本
```bash
uv python list --only-installed
# 如果沒有3.10.13版本請安裝
uv python install 3.10.13
# 安裝完後請指定使用3.10.13版本執行
uv python pin 3.10.13
# 使用uv創建虛擬環境.venv
uv venv --python=3.10.13
# 使用uv管控初始化
uv init --requirements=requirements.txt
# 使用uv安裝相依套件
uv pip install -r requirements.txt
# 使用uv啟動模組
uv run example.py
```
---