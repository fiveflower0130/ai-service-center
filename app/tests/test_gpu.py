# 建立診斷腳本
# filepath: gpu_diagnosis.py
import torch
import subprocess
import sys

def diagnose_gpu():
    print("=== GPU 診斷報告 ===")
    
    # PyTorch 資訊
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 是否可用: {torch.cuda.is_available()}")
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 數量: {torch.cuda.device_count()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"GPU {i} Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")
    else:
        print("❌ CUDA 不可用")
    
    # 測試 GPU 運算
    if torch.cuda.is_available():
        try:
            x = torch.randn(3, 3).cuda()
            y = torch.randn(3, 3).cuda()
            z = torch.mm(x, y)
            print("✅ GPU 運算測試成功")
        except Exception as e:
            print(f"❌ GPU 運算測試失敗: {e}")

if __name__ == "__main__":
    diagnose_gpu()