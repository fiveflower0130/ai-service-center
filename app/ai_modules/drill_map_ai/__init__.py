from .module import DrillMapAIModule

# 全域 AI 模組實例
_drill_ai_module = None

def get_drill_ai_module():
    """取得 DrillMapAI 模組實例"""
    global _drill_ai_module
    if _drill_ai_module is None:
        _drill_ai_module = DrillMapAIModule()
    return _drill_ai_module

def get_drill_ai_module_instance():
    """直接返回模組實例（用於 app.py 初始化）"""
    return get_drill_ai_module()

__all__ = ['DrillMapAIModule', 'get_drill_ai_module', 'get_drill_ai_module_instance']