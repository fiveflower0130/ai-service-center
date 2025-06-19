import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any, Awaitable
from icecream import ic
import cv2
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from cnocr import CnOcr
from scipy.linalg import inv
from autogluon.tabular import TabularPredictor
from torchvision import models,transforms
from PIL import Image

class DrillMapAIModule:
    # Initialize icecream for debugging
    ic.disable()
    # if os.getenv('PRODUCTION') == 1:
    #     ic.disable()
    # else:
    #     ic.enable()
    #     ic.configureOutput(includeContext=True, prefix='[DrillMapAI]->')

    def __init__(self):
        # 設定 icecream 的輸出
        self._ic = ic
        # 初始化 cnocr OCR 模型
        self._ocr = CnOcr(det_model_name='en_PP-OCRv3_det', rec_model_name='en_PP-OCRv3')
        # 設定裁切參數
        self._crop = {
            1: {'radius': (60, 600, 120, 150), 'stat': (210, 905, 437, 55), 'skip_idx': [2, 3, 13, 14, 24]},
            0: {'radius': (70, 600, 140, 150), 'stat': (270, 900, 370, 60), 'skip_idx': []},
            9: {'radius': (), 'stat':(210, 30, 360, 360), 'skip_idx': []}
        } 
        # 影像前處理工具(大小、轉換tensor、正規化)
        self._image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(), 
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        # 初始化 ResNet 模型
        self._resnet_model = None
        self._input_size = None
        # 設定使用模型的路徑
        self._data_model_folder = os.path.join(os.path.dirname(__file__), 'data_model')
        # 取得所有參考設定
        self._reference_config = self._get_reference_config()
        # 初始化所有統計資料
        self._model_stats = {}
        # abnormal 模型的預測結果
        self._abnormal_label = {0: "TYPE1", 1: "TYPE3", 2: "TYPE4"}
        # 初始化產品模型對應表
        self._product_model_map = {
            'A158200': 'A158200_',
            'A287570': 'A287570_',
            'A296960': 'A296960_',
            '1Q560-036306BO-B': '1Q560-036306BO-B',
            '1166_111_A244G_REV_A': '1166_111_A244G_REV_A',
            'I-G3683_C': 'I-G3683_C'
        }


    async def async_init(self):
        """
        初始化方法，確保在使用前已經載入所有必要的模型和統計資料
        """
        try:
            # 初始化 ResNet 模型
            self._resnet_model, self._input_size = await self._init_resnet_model(num_class=2, feature_extract=True)
            # 初始化所有統計資料
            await self._init_all_stats()
        except Exception as e:
            raise Exception(f"Initialization failed: {e}")
    
    def _get_reference_config(self)->Dict:
        """
        集中管理所有參考欄位、目標欄位、統計路徑等設定
        """
        # 基本模型欄位名稱
        model_col_names = [
            '半徑5','半徑10','半徑15','半徑20','半徑25','半徑30','半徑35','半徑40','半徑45','半徑50',
            '總點數','X軸平均值','X軸標準差','X軸規格上限','X軸規格下限','X軸Ca','X軸Cp','X軸CpK','X軸3Sigma','X軸Avg+3Sigma',
            'Y軸平均值','Y軸標準差','Y軸規格上限','Y軸規格下限','Y軸Ca','Y軸Cp','Y軸CpK','Y軸3Sigma','Y軸Avg+3Sigma',
            '偏移量平均值','偏移量標準差','偏移量規格上限','偏移量規格下限','製程標準度Ca','製程精密度Cp','製程能力CpK','製程3Sigma','製程Avg+3Sigma'
        ]
        # 模型欄位名稱包含標籤和路徑
        model_col_names_with_label = model_col_names + ['label', 'path']
        # 需要刪除的欄位名稱
        drop_cols = ['總點數', 'X軸規格上限', 'X軸規格下限', 'Y軸規格上限', 'Y軸規格下限', '偏移量規格上限', '偏移量規格下限']
        # 需要刪除的欄位名稱包含標籤和路徑
        drop_cols_with_label = drop_cols + ['label', 'path']
        # 目標欄位名稱
        target_columns = [
            'X軸平均值', 'X軸標準差', 'X軸規格上限', 'X軸規格下限', 'X軸Ca', 'X軸Cp', 'X軸CpK', 'X軸3Sigma', 'X軸Avg+3Sigma',
            'Y軸平均值', 'Y軸標準差', 'Y軸規格上限', 'Y軸規格下限', 'Y軸Ca', 'Y軸Cp', 'Y軸CpK', 'Y軸3Sigma', 'Y軸Avg+3Sigma',
            '偏移量平均值', '偏移量標準差', '偏移量規格上限', '偏移量規格下限' 
        ] + ['製程3Sigma', '製程Avg+3Sigma']
        # 目標欄位包含距離計算的欄位
        target_columns_with_distance = [
            'X軸平均值', 'X軸標準差', 'X軸規格上限', 'X軸規格下限', 'X軸Ca', 'X軸Cp', 'X軸CpK', 'X軸3Sigma', 'X軸Avg+3Sigma',
            'Y軸平均值', 'Y軸標準差', 'Y軸規格上限', 'Y軸規格下限', 'Y軸Ca', 'Y軸Cp', 'Y軸CpK', 'Y軸3Sigma', 'Y軸Avg+3Sigma',
            '偏移量平均值', '偏移量標準差', '偏移量規格上限', '偏移量規格下限', '製程標準度Ca', '製程精密度Cp', '製程能力CpK', '製程3Sigma', '製程Avg+3Sigma'
        ]
        # 模型欄位名稱
        model_stat_paths = {
            "A287570_": os.path.join(self._data_model_folder, "two_classification", "A287570_", "stat", "target.csv"),
            "A296960_": os.path.join(self._data_model_folder, "two_classification", "A296960_", "stat", "target.csv"),
            "A158200_": os.path.join(self._data_model_folder, "two_classification", "A158200_", "stat", "target.csv")
        }
        # 多分類模型路徑
        muti_classification_model_paths = {
            "A287570_":{
                "product": os.path.join(self._data_model_folder, "multi_classification", "A287570_", "multi_classification_Autogluon", "AsTwo", "A287570_", "A287570_"),
                "general": os.path.join(self._data_model_folder, "multi_classification", "A287570_", "multi_classification_Autogluon", "AsTwo", "A287570_", "general"),
                "abnormal": os.path.join(self._data_model_folder, "multi_classification", "A287570_", "multi_classification_Autogluon", "AsThree", "A287570_", "general")
            },
            "A296960_":{
                "product": os.path.join(self._data_model_folder, "multi_classification", "A296960_", "multi_classification_Autogluon", "AsTwo", "A296960_", "A296960_"),
                "general": os.path.join(self._data_model_folder, "multi_classification", "A296960_", "multi_classification_Autogluon", "AsTwo", "A296960_", "general"),
                "abnormal": os.path.join(self._data_model_folder, "multi_classification", "A296960_", "multi_classification_Autogluon", "AsThree", "A296960_", "general")
            },
            "A158200_":{
                "product": os.path.join(self._data_model_folder, "multi_classification", "A158200_", "multi_classification_Autogluon", "AsTwo", "A158200_", "A158200_"),
                "general": os.path.join(self._data_model_folder, "multi_classification", "A158200_", "multi_classification_Autogluon", "AsTwo", "A158200_", "general"),
                "abnormal": os.path.join(self._data_model_folder, "multi_classification", "A158200_", "multi_classification_Autogluon", "AsThree", "A158200_", "general")
            }
        }
        # 二分類圖片模型路徑
        two_classification_image_model_paths = {
            "A287570_": os.path.join(self._data_model_folder, "two_classification", "A287570_", "weight", "target", "model_best.pth.tar"),
            "A296960_": os.path.join(self._data_model_folder, "two_classification", "A296960_", "weight", "target", "model_best.pth.tar"),
            "A158200_": os.path.join(self._data_model_folder, "two_classification", "A158200_", "weight", "target", "model_best.pth.tar")
        }

        return {
            "model_col_names": model_col_names,
            "model_col_names_with_label": model_col_names_with_label,
            "drop_cols": drop_cols,
            "drop_cols_with_label": drop_cols_with_label,
            "target_columns": target_columns,
            "target_columns_with_distance": target_columns_with_distance,
            "model_stat_paths": model_stat_paths,
            "muti_classification_model_paths": muti_classification_model_paths,
            "two_classification_image_model_paths": two_classification_image_model_paths,
        }
    
    async def _init_resnet_model(self, num_class:int=2, feature_extract:bool=True) -> Awaitable[Tuple[nn.Module, int]]:
        """
        初始化 ResNet 模型 目前只有用到18
        :return: resnet 模型實例, input_size
        """
        try:
            # 檢查是否有可用的 GPU
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._ic(f"Using device: {device}")
            # 初始化 ResNet 模型
            model_ft = models.resnet18(weights="IMAGENET1K_V1")
            # 設定是否凍結參數
            if feature_extract:
                for param in model_ft.parameters():
                    param.requires_grad = False
            # 修改最後一層全連接層
            num_ftrs = model_ft.fc.in_features
            model_ft.fc = nn.Linear(num_ftrs, num_class)
            # 將模型移動到指定設備
            model_ft = model_ft.to(device)
            # 設定輸入大小
            input_size = 224
            self._ic(f"Initialized ResNet model with {num_class} classes and input size {input_size}")
            return model_ft, input_size
            
        
        except Exception as e:
            raise e
    
    async def _init_all_stats(self):
        """
        初始化一次性載入所有統計資料到self._model_stats 
        這些統計資料將用於後續的馬氏距離計算和模型判斷
        """
        ref = self._reference_config
        for model_key in ref["model_stat_paths"]:
            model_shape = await self._load_and_prepare_stat(model_key)
            if model_shape.empty:
                raise ValueError(f"No data available for model {model_key}. Please check the statistics file.")
            self._model_stats[model_key]  = model_shape
    
    async def _load_and_prepare_stat(self, model_key: str) -> pd.DataFrame:
        """
        讀取並準備統計數據
        :param model_key: 模型名稱
        :return: 準備好的 DataFrame
        """
        try:
            # 如果已經載入過，直接返回已有的值
            if model_key in self._model_stats:
                return self._model_stats[model_key]
            
            # 讀取統計資料
            ref = self._reference_config
            df = pd.read_csv(ref["model_stat_paths"][model_key], header=None)
            df.columns = ref["model_col_names_with_label"]

            # 跳過第一列（通常是標題或說明），並做型別轉換
            df = df.iloc[1:].applymap(self._value_conversion)
            df.reset_index(drop=True, inplace=True)

            # 單位調整：偏移量規格上限 < 10 時，目標欄位 * 1000
            for i in range(len(df)):
                if df.iloc[i]['偏移量規格上限'] < 10:
                    df.loc[i, ref["target_columns_with_distance"]] = df.loc[i, ref["target_columns_with_distance"]] * 1000

            # 將 label 欄位轉為 int 型別
            df['label'] = df['label'].astype(int)
            self._ic(f"Loaded statistics for {model_key} with shape {df.shape}")

            # 返回準備好的 DataFrame
            return df
        
        except Exception as e:
            self._ic(f"Error loading statistics for {model_key}: {e}")
            return pd.DataFrame()
    
    def _get_file_version(self, file_path: str) -> int:
        """
        根據檔案修改日期判斷 file_ver
        """
        try:
            file_modified_time = os.path.getmtime(file_path)
            file_modified_date = datetime.fromtimestamp(file_modified_time)
            return 0 if file_modified_date < datetime(2024, 1, 25) else 1
        except Exception as e:
            return -1  # 返回 -1 表示無法判斷版本

    def _remove_black(self, image:np.ndarray, threshold:int=173) -> np.ndarray:
        """
        將圖片中與黑色相近的部分去除，將其轉為白色
        :param image: 原始圖片
        :param threshold: 黑色區域的閾值，可微調，數值越大越嚴格
        :return: 處理後的圖片
        """
        white = np.array([255, 255, 255], dtype=np.uint8)
        black = np.array([0, 0, 0], dtype=np.uint8)

        # # 使用 np 內建公式計算每個像素與黑色的平方差
        # diff = np.sum(np.square(image.astype(np.int32) - black), axis=2)  # 計算每個像素與黑色的平方差
        # mask = diff < (threshold ** 2)

        # 使用np內建公式計算每個像素與黑色的歐氏距離
        diff = np.linalg.norm(image.astype(np.int16) - black, axis=2)
        mask = diff < threshold

        result = image.copy()
        result[mask] = white
        return result
    
    def _keep_pink(self, image: np.ndarray, threshold:int=210) -> np.ndarray:
        """
        只保留接近粉紅色的像素，其餘設為白色
        :param image: 原始圖片
        :param threshold: 粉紅色區域的閾值，可微調，數值越小越嚴格
        :return: 處理後的圖片
        
        """
        pink = np.array([255, 0, 255], dtype=np.uint8)

        # 使用np內建公式計算每個像素與黑色的歐氏距離
        diff = np.linalg.norm(image.astype(np.int16) - pink, axis=2)
        mask = diff < threshold

        result = np.ones_like(image) * 255  # 先全白
        result[mask] = image[mask]          # 粉紅色區塊保留原色
        return result
    
    def _keep_green(self, image: np.ndarray, threshold:int=250) -> np.ndarray:
        """
        只保留接近綠色的像素，其餘設為白色
        :param image: 原始圖片
        :param threshold: 綠色區域的閾值，可微調，數值越小越嚴格
        :return: 處理後的圖片
        """
        green = np.array([0, 255, 0], dtype=np.uint8)

        # 使用np內建公式計算每個像素與黑色的歐氏距離
        # 計算每個像素與綠色的歐氏距離
        diff = np.linalg.norm(image.astype(np.int16) - green, axis=2)
        mask = diff < threshold

        result = np.ones_like(image) * 255  # 先全白
        result[mask] = image[mask]          # 綠色色區塊保留原色
        return result
    
    def _keep_pink_and_green(self, image: np.ndarray, pink_threshold:int=200, green_threshold:int=200) -> np.ndarray:
        """
        同時保留接近粉紅色與綠色的像素，其餘設為白色
        :param image: 原始圖片
        :param pink_threshold: 粉紅色區域的閾值
        :param green_threshold: 綠色區域的閾值
        :return: 處理後的圖片
        """
        pink = np.array([255, 0, 255], dtype=np.uint8)
        green = np.array([0, 255, 0], dtype=np.uint8)

        # 計算每個像素與粉紅色的歐氏距離
        diff_pink = np.linalg.norm(image.astype(np.int16) - pink, axis=2)
        mask_pink = diff_pink < pink_threshold

        # 計算每個像素與綠色的歐氏距離
        diff_green = np.linalg.norm(image.astype(np.int16) - green, axis=2)
        mask_green = diff_green < green_threshold

        # 合併兩個 mask
        mask = np.logical_or(mask_pink, mask_green)

        # 先全白
        result = np.ones_like(image) * 255
        # 保留粉紅色與綠色區塊
        result[mask] = image[mask]
        return result
    
    def _clean_ocr_value(self, value:str) -> float:
        """
        清理 OCR 辨識的結果，將其轉換為 float 型別
        :param value: OCR 辨識的結果
        :return: 清理後的結果
        """
        # 清理 OCR 結果字串，轉 float
        if not isinstance(value, str):
            return value
        try:
            is_percent = '%' in value
            value = value.replace(' ', '').replace('%', '')
            # value = value.strip().replace(' ', '').replace('%', '')
            # value = value.replace('O', '0').replace('G', '6')
            value = value.replace('O', '0').replace('G', '6').replace('l', '1').replace('I', '1').replace('A', '7').replace('il', '11')
            value = '0' + value if value.startswith('.') else value
            # 修正負號處理
            if '-' in value:
                value ='-' + value[1:].replace('-', '.') if value.startswith('-') else value.replace('-', '.')
            # replace_dict = {'il': '11', 'A': '7', 'l': '1', 'I': '1'}
            # value = replace_dict.get(value, value)
            result = float(value)
            # return float(value) / 100 if '%' in value else float(value)
            return result / 100 if is_percent else result
        
        except Exception as e:
            self._ic(f"Error cleaning OCR value: {e}")
            return -1
    
    def _compute_mahalanobis(self, ocr_input: pd.DataFrame, stats: dict) -> dict:
        """
        計算馬氏距離
        :param ocr_df: OCR 辨識結果的 DataFrame
        :param stats: 統計資料
        :return: 馬氏距離字典
        """
        
        distances = {}
        for model_key, df in stats.items():
            if df.empty:
                self._ic(f"No data available for model {model_key} after filtering.")
                return distances
            
            # 取得輸入向量
            input_vec = np.array(ocr_input[df.columns].iloc[0])
            # 取得參考向量
            ref_vec = df.median() if model_key == "A287570_" else df.mean()
            # 計算協方差矩陣的逆轉
            inv_cov = inv(np.cov(df, rowvar=False))
            
            # 計算馬氏距離
            diff = ref_vec - input_vec
            distances[model_key] = float(np.sqrt(diff.T.dot(inv_cov).dot(diff))) 

        # 返回所有模型的馬氏距離  
        return distances
    
    def _value_conversion(self, value: str) -> int|float|str:
        """
        轉換函數，將字串轉換為 int、float 或保留原字串
        :param value: 要轉換的值
        :return: 轉換後的值
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    
    async def _preprocess_image(self, img_path:str)-> Awaitable[Image.Image]:
        """
        圖片預處理，將圖片內與黑色相近的部分去除，在轉成PIL Image 格式後輸出
        :param img_path: 圖片路徑
        :return: 預處理後的圖片路徑
        """
        try:
            # 讀取圖片
            img = cv2.imread(img_path)
            if img is None:
                self._ic(f"Failed to read image: {img_path}")
                return None
            
            # 對圖片進行切割處理並去除黑色區域
            crop_params = self._crop[9].get('stat')# 定義裁切參數
            x, y, h, w = crop_params
            crop_img = img[x:x+h, y:y+w]
            # crop_img_block = self._remove_black(crop_img)
            # crop_img_pink = self._keep_pink(crop_img)
            # crop_img_green = self._keep_green(crop_img)
            crop_img_pink_green = self._keep_pink_and_green(crop_img)

            # # 保留處理後的圖片
            # base_name = os.path.basename(img_path)
            # img_name = base_name.split('.')[0]
            # cv2.imwrite(f"{self._data_model_folder}/inference/{img_name}.png", crop_img_pink_green)
            # # image_path = f"{self._data_model_folder}/inference/{img_name}.png"
            # # return image_path

            # 將處理後的圖片轉為 RGB 格式(對應原本使用PIL Image讀取給torch model使用)
            rgb_image = cv2.cvtColor(crop_img_pink_green, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)

            return pil_image

            
        
        except Exception as e:
            self._ic(f"Error preprocessing image {img_path}: {e}")
            return None
    
    async def _cnocr_inference(self, file:str)-> Awaitable[Optional[pd.DataFrame]]:
        """
        使用 cnocr 進行 OCR 辨識，並將結果整理成 DataFrame 格式
        :param image: 圖片或圖片列表 
        :param file_ver: 版本號，1 為舊版，0 為新版
        :return: DataFrame with OCR results
        """
        
        dff = pd.DataFrame()

        # 定義裁切參數
        crop_params = self._crop
        
        # 判定檔案版本
        file_ver = self._get_file_version(file)
        if file_ver == -1:
            self._ic(f"Unable to determine file version for: {file}. Please check the file.")
            return dff
        
        # 取得裁切參數
        params =crop_params.get(file_ver, None)  # Default to version 1 if not found 
        if params is None:
            self._ic(f"Unsupported file version: {file_ver}. Please check the file.")
            return dff

        # 讀取圖片並進行 OCR 辨識並判斷圖片格式是否正確
        img = cv2.imread(file)
        if not isinstance(img, np.ndarray):
            self._ic(f"Invalid image format for file: {file}. Please check the file.")
            return dff
        
        # 讀取圖片並進行 OCR 辨識
        try:
            # 半徑區域 OCR
            radius_out = await self._ocr_crop(img, params['radius'], gray=False, resize=True)
            radius = [r['text'] for r in radius_out]

            # 統計區域 OCR
            stat_out = await self._ocr_crop(img, params['stat'], gray=True, resize=False)
            stat = [s['text'] for idx, s in enumerate(stat_out) if idx not in params['skip_idx']]
                
            # 合併結果
            row = radius[1::2] + stat
            df = pd.DataFrame([row])

            # 欄位資料清理
            for col in df.columns:
                df[col] = df[col].map(self._clean_ocr_value)
        
            dff = pd.concat([dff, df], ignore_index=True)
        except Exception as e:
            # 檢查是否有資料
            if dff.empty:
                self._ic("No valid OCR data found.")

        return dff
    
    async def _ocr_crop(self, img:np.ndarray, crop:Tuple[int, int, int, int], gray:bool=False, resize:bool=False)-> Awaitable[List]:
        """
        裁切圖片
        :param img: 原始圖片
        :param cropx: [裁切區域的x座標, 裁切區域的y座標, 裁切區域的高度, 裁切區域的寬度]
        :param gray: 是否轉為灰階圖片
        :return: 裁切後的圖片
        """
        if not self._ocr:
            raise ValueError("OCR model is not loaded correctly.")
        
        x, y, h, w = crop
        crop_img = img[x:x+h, y:y+w]
        if gray:
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        if resize:
            crop_img = cv2.resize(crop_img, (200, 205), interpolation=cv2.INTER_AREA)
        return self._ocr.ocr(crop_img)
    
    async def _get_image_prediction(self, model_path:str, pil_image:Image) -> Awaitable[Tuple[str, float]]:
        """
        對圖片進行處理之後再使用 torch 進行圖片預測
        :param model_path: 圖片模型路徑
        :param image_path: 圖片路徑
        :return: 預測結果標籤和概率
        """
        try:
            # # 使用PIL讀取圖片內容
            # pil_image = Image.open(image_path)

            # 將圖片轉換為 tensor 供touch模型使用
            tensor_batch = self._image_transform(pil_image).unsqueeze(0)  # 增加 batch 維度，批次大小為 1

            # 獲取圖像模型狀態字典
            touch_model = torch.load(model_path) # 讀取模型
            model_state_dict = touch_model.get('model_state_dict', [])  # 獲取模型狀態字典

            # 檢查模型狀態字典是否為字典類型
            if not model_state_dict:
                raise ValueError(f"Model state dict not found in {model_path}.")
                 
            # 將模型狀態字典載入模型並設定為評估模式
            model = self._resnet_model
            model.load_state_dict(model_state_dict) # 將模型狀態字典載入模型
            # 設置模型為評估模式
            model.eval()  

            # 將輸入張量移動到模型上
            with torch.no_grad():
                output = model(tensor_batch)
                
            # 檢查輸出形狀是否符合預期
            probabilities = torch.nn.functional.softmax(output, dim=1)

            # 檢查模型是否為二分類模型
            if probabilities.shape[1] != 2:
                raise ValueError(f"Model output shape {probabilities.shape} does not match expected shape for binary classification.")
            
            # 獲取預測標籤和概率
            predicted_prob, predicted_class = torch.max(probabilities, 1)

            # 取得預測標籤和概率
            label = "正常" if predicted_class.item() == 0 else "異常"

            return label, predicted_prob.item()  # 返回標籤和預測概率
        
        except Exception as e:
            self._ic(f"Error during image prediction: {e}")
            return None, None
    
    async def _get_tablular_prediction(self, model_path:str, ocr_df:pd.DataFrame, abnormal:bool=False) -> Awaitable[Tuple[str, float]]:
        """
        使用 TabularPredictor 進行預測
        :param model_path: 模型路徑
        :param ocr_df: OCR 辨識結果的 DataFrame
        :param abnormal: 是否為異常預測
        :return: 處理 AutoGluon DataFrame 可能回傳的值，並返回預測標籤和概率。
        """
        
        # 處理AutoGluon DataFrame 可能回傳的值
        def _get_first_value(obj):
            if hasattr(obj, 'iloc'):
                # DataFrame or Series
                try:
                    return obj.iloc[0, 0]  # DataFrame格式
                except:
                    return obj.iloc[0]     # Series格式
            elif hasattr(obj, 'tolist'):
                arr = obj.tolist()
                return arr[0][0] if isinstance(arr[0], (list, np.ndarray)) else arr[0]
            elif isinstance(obj, (list, np.ndarray)):
                return obj[0][0] if isinstance(obj[0], (list, np.ndarray)) else obj[0]
            else:
                return obj  # scalar

        try:
            # 讀取模型
            predictor = TabularPredictor.load(model_path)
            # 預測
            prediction = predictor.predict(ocr_df)
            pred_value = _get_first_value(prediction)  # 獲取預測值
            
            if abnormal:
                prediction_prob = predictor.predict_proba(ocr_df, as_multiclass=True)
                prob_value = _get_first_value(prediction_prob)  # 獲取預測概率
                # 根據預測結果選擇標籤
                label = self._abnormal_label.get(pred_value, "TYPE999")
            else:
                prediction_prob = predictor.predict_proba(ocr_df, as_multiclass=False)
                prob_value = _get_first_value(prediction_prob)
                label = "正常" if pred_value == 0 else "異常"

            return label, prob_value  # 返回標籤和預測概率
            
        except Exception as e:
            self._ic(f"Error during prediction: {e}")
            return None, None

    async def get_graph_mahalanobis_and_model(self, ocr_df:pd.DataFrame) -> Tuple[str, float]:
        """
        計算圖形的馬氏距離並判定其接近的模組類型
        :param file: 圖片路徑
        :return: 與圖片標最接近距離的模型名稱和馬氏距離
        """
        
        # 設定欄位名稱
        ref = self._reference_config
        ocr_df.columns = ref["model_col_names"]

        # 載入統計資料
        stats = self._model_stats
        drop_cols_with_label = ref["drop_cols_with_label"]  
        # stats_summaries = {k: self._get_stat_summary(v, 0, drop_cols) for k, v in stats.items()}
        stats_normal = {k: v[v['label'] == 0].drop(drop_cols_with_label, axis=1) for k, v in stats.items()}

        # 強制ocr順序與stats一致
        filter_drop_cols = ref["drop_cols"]
        filter_ocr_input = ocr_df.drop(filter_drop_cols, axis=1)

        # # 統計量（A287570_用median，A296960_和A158200_用mean，與原本一致）
        # medians = {k: df.median() for k, df in stats_normal.items()}
        # means = {k: df.mean() for k, df in stats_normal.items()}

        # # 計算斜方差矩陣的逆轉
        # inv_covs = {
        #     "A287570_": inv(np.cov(stats_normal["A287570_"], rowvar=False)),
        #     "A296960_": inv(np.cov(stats_normal["A287570_"], rowvar=False)),
        #     "A158200_": inv(np.cov(stats_normal["A287570_"], rowvar=False)),
        # }
        
        # # 強制順序一致
        # filter_drop_cols = ['總點數','X軸規格上限','X軸規格下限','Y軸規格上限','Y軸規格下限','偏移量規格上限','偏移量規格下限']
        # filter_ocr_input = ocr_df.drop(filter_drop_cols, axis=1)
        # input_vec_A287570 = np.array(filter_ocr_input[stats_normal["A287570_"].columns].iloc[0])
        # input_vec_A296960 = np.array(filter_ocr_input[stats_normal["A296960_"].columns].iloc[0])
        # input_vec_A158200 = np.array(filter_ocr_input[stats_normal["A158200_"].columns].iloc[0])

        # distances = {
        #     "A287570_": self._compute_mahalanobis_old(input_vec_A287570, np.array(medians["A287570_"]), inv_covs["A287570_"]),
        #     "A296960_": self._compute_mahalanobis_old(input_vec_A296960, np.array(means["A296960_"]), inv_covs["A296960_"]),
        #     "A158200_": self._compute_mahalanobis_old(input_vec_A158200, np.array(means["A158200_"]), inv_covs["A158200_"])
        # }
        
        # 計算馬氏距離
        distances = self._compute_mahalanobis(filter_ocr_input, stats_normal)
        if not distances:
            return None, float('inf')

        # 找出距離最小的型號
        best_model = min(distances, key=distances.get)
        return best_model, distances[best_model]

    async def get_graph_multiClassification(self, product_type:str, img_src:str, ocr_df:pd.DataFrame) -> str:
        """
        對圖形進行三個二分類分模型的預測(對應圖號模型、常規模型、圖像模型)，若其中一個預測有出現"異常"則進行異常多分類推理
        :param product_type: 產品類型（如 A287570_、A296960_、A158200_）
        :param img_src: 圖片路徑
        :param ocr_df: OCR 辨識結果的 DataFrame
        :return: 預測結果
        """
        # 內部檢測方法用來統一處理二分類+異常多分類
        async def _predict_and_check_abnormal(model_path, ocr_df, abnormal_model_path, abnormal=True):
            if not os.path.exists(model_path):
                self._ic(f"Model path does not exist: {model_path}")
                return None
            
            label, prob = await self._get_tablular_prediction(model_path, ocr_df, abnormal=False)
            self._ic(f"Label: {label}, Prob: {prob}")
            if label is None or prob is None:
                self._ic(f"Failed to get prediction for model: {model_path}")
                return None

            if label == "異常":
                ab_label, ab_prob = await self._get_tablular_prediction(abnormal_model_path, ocr_df, abnormal=abnormal)
                self._ic(f"Abnormal Label: {ab_label}, Abnormal Prob: {ab_prob}")
                if ab_label is None or ab_prob is None:
                    self._ic(f"Failed to get abnormal prediction for model: {abnormal_model_path}")
                    return None
                
                return ab_label
            
            return None

        ref = self._reference_config
        classification_result = "TYPE0"
        
        # 對應欄位名稱
        ocr_df.columns = ref["model_col_names"]
        ocr_df['panel_path'] = ocr_df['panel_path'].astype(str) if 'panel_path' in ocr_df.columns else ""
        
        # 對ocr_df進行必要的欄位處理
        if ocr_df.iloc[0]['偏移量規格上限'] < 10:
            target_columns = ref["target_columns"]
            ocr_df.loc[0, target_columns] = ocr_df.loc[0, target_columns] * 1000

        abnormal_model_path = ref["muti_classification_model_paths"][product_type]["abnormal"]
        
        # 1. 對應圖號模型
        product_model_path = ref["muti_classification_model_paths"][product_type]["product"]
        # 檢查模型路徑是否存在
        if not os.path.exists(product_model_path):
            self._ic(f"{product_type} Model path does not exist.")
            return None
        
        product_result = await _predict_and_check_abnormal(product_model_path, ocr_df, abnormal_model_path)
        if product_result is not None:
            self._ic(f"Product Result: {product_result}")
            return product_result
        
        # 2. 常規模型
        general_model_path = ref["muti_classification_model_paths"][product_type]["general"]
        # 檢查模型路徑是否存在
        if not os.path.exists(general_model_path):
            self._ic(f"{product_type} General model path does not exist.")
            return None
        
        general_result = await _predict_and_check_abnormal(general_model_path, ocr_df, abnormal_model_path)
        if general_result is not None:
            self._ic(f"General Result: {general_result}")
            return general_result
        
        # 3. 圖像模型
        image_model_path = ref["two_classification_image_model_paths"][product_type]
        # 檢查模型路徑是否存在
        if not os.path.exists(image_model_path):
            self._ic(f"{product_type} Image model path does not exist.")
            return None
        
        # 使進行圖像處理
        img_preprocess = await self._preprocess_image(img_src)
        if img_preprocess is None:
            self._ic(f"Failed to preprocess image for {product_type}.")
            return None
        
        # 對圖片預測處理
        image_label, image_prob = await self._get_image_prediction(image_model_path, img_preprocess)
        self._ic(f"Label: {image_label}, Prob: {image_prob}")
        if image_label is None or image_prob is None:
            self._ic(f"Failed to get prediction for {product_type} image model.")
            return None
        
        if image_label == "異常":
            image_abnormal_label, image_abnormal_prob = await self._get_tablular_prediction(abnormal_model_path, ocr_df, abnormal=True)
            self._ic(f"Abnormal Label: {image_abnormal_label}, Abnormal Prob: {image_abnormal_prob}")
            if image_abnormal_label is None or image_abnormal_prob is None:
                self._ic(f"Failed to get prediction for {product_type} image abnormal model.")
                return None
            return image_abnormal_label
        
        return classification_result

    async def get_ai_classification(self, img_src:str, product_name:str) -> Awaitable[dict]:
        
        product_name_mapping = self._product_model_map
        product_model = product_name_mapping.get(product_name, 'unknown')
        # 檢查圖片是否存在
        if os.path.exists(img_src):
            try:
                ocr_df = await self._cnocr_inference(img_src)
                # 檢查 OCR 結果是否為空
                if ocr_df.empty:
                    raise Exception(f"OCR result is empty for image: {img_src}. Please check the image or OCR model.")
                
                # 依據產品名稱進行對應的處理方式
                if product_model == 'unknown':
                    presume_model, mahalanobis = await self.get_graph_mahalanobis_and_model(ocr_df)
                    if presume_model is None:
                        raise Exception(f"Failed to classify image: {img_src}. No valid model found.")
                    if mahalanobis == float('inf'):
                        raise Exception(f"Failed to classify image: {img_src}. Distance is infinite.")
                    # presume_model = 'A287570_'
                    # mahalanobis = 34.691369
                    
                    if mahalanobis > 150: 
                        classification_code = 'UNKNOW'
                    else:
                        classification_code = await self.get_graph_multiClassification(presume_model, img_src, ocr_df)
                        if classification_code is None:
                            raise Exception(f"Failed to classify image. No valid classification code found.")

                    result = {"classification_code": classification_code, "classification_model": presume_model, "distance": format(mahalanobis, '.6f')}

                else:
                    classification_code = await self.get_graph_multiClassification(product_model, img_src, ocr_df)
                    result = {"classification_code": classification_code, "classification_model": product_model, "distance": -1} #-1 表示沒有馬氏距離計算

            except Exception as e:
                self._ic(f"Error processing image[{img_src}]: {e}")
                result = {"classification_code": "ERROR", "classification_model": product_model, "distance": -1} # ERROR 表示處理過程中出現錯誤

        else:
            self._ic(f"Image[{img_src}] not found.")
            result = {"classification_code": "N/A", "classification_model": product_model, "distance": -1} # N/A 表示圖片不存在

        return result
    