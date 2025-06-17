import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import pandas as pd
import numpy as np
import os

# 假設 DrillMapAIModule 在 drill_map_module.py 中
from ai_modules.drill_map_ai.module import DrillMapAIModule

# 以下是測試用的 fixture 和測試函數的一個範例，整個測試模組需要根據實際情況進行調整(尚未包含所有測試用例)
@pytest.fixture
def module():
    m = DrillMapAIModule()
    # mock 內部依賴
    m._ic = MagicMock()
    m._product_model_map = {'A287570_': 'A287570_'}
    m._reference_config = m._get_reference_config()
    m._model_stats = {'A287570_': pd.DataFrame(np.ones((2, 10)), columns=[f'col{i}' for i in range(10)])}
    m._crop = {0: {'radius': (0,0,10,10), 'stat': (0,0,10,10), 'skip_idx': []}, 1: {'radius': (0,0,10,10), 'stat': (0,0,10,10), 'skip_idx': []}, 9: {'stat': (0,0,10,10)}}
    m._ocr = MagicMock()
    m._image_transform = MagicMock(return_value=np.zeros((3, 224, 224)))
    m._resnet_model = MagicMock()
    m._abnormal_label = {0: 'TYPE0', 1: 'TYPE1'}
    m._data_model_folder = '.'
    return m

def test_image_not_found(module):
    result = pytest.run(module.get_ai_classification('not_exist.jpg', 'A287570_'))
    assert result['classification_code'] == 'N/A'

def test_ocr_empty(module):
    with patch('os.path.exists', return_value=True):
        module._cnocr_inference = AsyncMock(return_value=pd.DataFrame())
        result = pytest.run(module.get_ai_classification('test.jpg', 'A287570_'))
        assert result['classification_code'] == 'ERROR'

def test_unknown_product_model(module):
    with patch('os.path.exists', return_value=True):
        module._cnocr_inference = AsyncMock(return_value=pd.DataFrame(np.ones((1,10))))
        module.get_graph_mahalanobis_and_model = AsyncMock(return_value=('A287570_', 100.0))
        module.get_graph_multiClassification = AsyncMock(return_value='TYPE0')
        result = pytest.run(module.get_ai_classification('test.jpg', 'unknown_name'))
        assert result['classification_code'] == 'TYPE0'

def test_mahalanobis_too_large(module):
    with patch('os.path.exists', return_value=True):
        module._cnocr_inference = AsyncMock(return_value=pd.DataFrame(np.ones((1,10))))
        module.get_graph_mahalanobis_and_model = AsyncMock(return_value=('A287570_', 200.0))
        result = pytest.run(module.get_ai_classification('test.jpg', 'unknown_name'))
        assert result['classification_code'] == 'UNKNOW'

def test_normal_flow(module):
    with patch('os.path.exists', return_value=True):
        module._cnocr_inference = AsyncMock(return_value=pd.DataFrame(np.ones((1,10))))
        module.get_graph_multiClassification = AsyncMock(return_value='TYPE0')
        result = pytest.run(module.get_ai_classification('test.jpg', 'A287570_'))
        assert result['classification_code'] == 'TYPE0'
