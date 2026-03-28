from .manager import generate_contract, review_contract

try:
    from .feishu_integration import ContractFeishuIntegration
    FEISHU_AVAILABLE = True
except ImportError:
    ContractFeishuIntegration = None
    FEISHU_AVAILABLE = False

__all__ = ["generate_contract", "review_contract"]
if FEISHU_AVAILABLE:
    __all__.append("ContractFeishuIntegration")
