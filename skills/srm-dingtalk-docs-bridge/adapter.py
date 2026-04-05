"""钉钉文档适配器"""


class DingTalkTemplateAdapter:
    """将通用模板转换为钉钉文档格式"""
    
    def __init__(self):
        from .template_generator import ContractTemplateGenerator
    
        self.template = ContractTemplateGenerator()

    def generate_contract_draft(self, title: str, contract_data: dict) -> str:
        """生成合同草稿（钉钉格式）"""
        return self.template.generate_contract_draft(title, contract_data)

    def generate_audit_report(self, contract_title: str, audit_results: dict) -> str:
        """生成审核报告（钉钉格式）"""
        return self.template.generate_audit_report(contract_title, audit_results)

    def generate_invoice_match_report(
        self, 
        po_number: str, 
        match_result: dict
    ) -> str:
        """生成三单匹配报告（钉钉格式）"""
        return self.template.generate_invoice_match_report(po_number, match_result)