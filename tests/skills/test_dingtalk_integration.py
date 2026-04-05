"""Tests for dingtalk client and adapter."""
import pytest
from skills.srm_dingtalk_docs_bridge.config import DingTalkConfig
from skills.srm_dingtalk_docs_bridge.adapter import DingTalkTemplateAdapter


def test_config_initialization():
    """测试 DingTalkConfig 初始化。"""
    config = DingTalkConfig(
        app_key="test_app_key",
        app_secret="test_app_secret",
    )
    
    assert config.app_key == "test_app_key"
    assert config.app_secret == "test_app_secret"
    assert config.base_url == "https://oapi.dingtalk.com"
    assert config.default_folder_token is None


def test_adapter_contracts_generation():
    """测试适配器生成合同草稿。"""
    adapter = DingTalkTemplateAdapter()
    content = adapter.generate_contract_draft(
        title="测试合同",
        contract_data={"supplier_name": "测试公司"},
    )
    
    assert "测试合同" in content
    assert "测试公司" in content
    assert "合同条款" in content or "基本信息" in content


def test_adapter_audit_report():
    """测试适配器生成审核报告。"""
    adapter = DingTalkTemplateAdapter()
    content = adapter.generate_audit_report(
        contract_title="测试合同",
        audit_results={
            "summary": "审核完成",
            "risks": [],
        }
    )
    
    assert "审核报告" in content
    assert "测试合同" in content


def test_adapter_invoice_match():
    """测试适配器生成三单匹配报告。"""
    adapter = DingTalkTemplateAdapter()
    content = adapter.generate_invoice_match_report(
        po_number="PO-001",
        match_result={
            "status": "MATCHED",
            "match_score": 1.0,
        }
    )
    
    assert "匹配报告" in content
    assert "PO-001" in content