from .matcher import match_three_way, verify_invoice_locally, generate_match_report

try:
    from .feishu_integration import InvoiceMatcherFeishuIntegration
    FEISHU_AVAILABLE = True
except ImportError:
    InvoiceMatcherFeishuIntegration = None
    FEISHU_AVAILABLE = False

__all__ = ["match_three_way", "verify_invoice_locally", "generate_match_report"]
if FEISHU_AVAILABLE:
    __all__.append("InvoiceMatcherFeishuIntegration")
