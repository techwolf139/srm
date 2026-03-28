"""飞书API客户端"""
import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class FeishuDocument:
    """飞书文档对象"""
    doc_id: str
    title: str
    url: str
    version: int
    created_time: int
    modified_time: int


class FeishuAPIError(Exception):
    """飞书API错误"""


class FeishuClient:
    """飞书开放平台API客户端"""

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        base_url: str = "https://open.feishu.cn/open-apis",
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self._tenant_access_token: Optional[str] = None
        self._token_expire: int = 0

    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        if self._tenant_access_token and time.time() < self._token_expire:
            return self._tenant_access_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        response = requests.post(
            url,
            json={"app_id": self.app_id, "app_secret": self.app_secret},
        )

        data = response.json()
        if data.get("code") != 0:
            raise FeishuAPIError(f"获取token失败: {data}")

        self._tenant_access_token = data["tenant_access_token"]
        self._token_expire = time.time() + data.get("expire", 7200) - 300
        return self._tenant_access_token

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_tenant_access_token()}"

        response = requests.request(method, url, headers=headers, **kwargs)
        data = response.json()

        if data.get("code") != 0:
            raise FeishuAPIError(f"API调用失败: {data}")

        return data

    def create_document(
        self, title: str, content: str, folder_token: Optional[str] = None
    ) -> FeishuDocument:
        """创建飞书文档"""
        endpoint = "/docx/v1/documents"
        payload: Dict[str, Any] = {"title": title}
        if folder_token:
            payload["folder_token"] = folder_token

        response = self._request("POST", endpoint, json=payload)
        doc_data = response["data"]

        doc_id = doc_data["document"]["document_id"]
        self._add_document_content(doc_id, content)

        return FeishuDocument(
            doc_id=doc_id,
            title=title,
            url=f"https://xxx.feishu.cn/docx/{doc_id}",
            version=1,
            created_time=doc_data["document"]["create_time"],
            modified_time=doc_data["document"]["modify_time"],
        )

    def _add_document_content(self, doc_id: str, content: str) -> None:
        """向文档添加内容"""
        endpoint = f"/docx/v1/documents/{doc_id}/blocks"
        blocks = self._markdown_to_blocks(content)
        self._request("POST", endpoint, json={"blocks": blocks, "index": 0})

    def _markdown_to_blocks(self, markdown: str) -> list:
        """将Markdown转换为飞书文档块"""
        blocks = []
        for line in markdown.split("\n"):
            if line.startswith("# "):
                blocks.append(
                    {
                        "block_type": 2,
                        "heading1": {"elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}},
                    }
                )
            elif line.startswith("## "):
                blocks.append(
                    {
                        "block_type": 3,
                        "heading2": {"elements": [{"type": "text_run", "text_run": {"content": line[3:]}}], "style": {}},
                    }
                )
            elif line.startswith("### "):
                blocks.append(
                    {
                        "block_type": 4,
                        "heading3": {"elements": [{"type": "text_run", "text_run": {"content": line[4:]}}], "style": {}},
                    }
                )
            elif line.startswith("-"):
                blocks.append(
                    {
                        "block_type": 14,
                        "bullet": {"elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}},
                    }
                )
            elif line.startswith("| "):
                blocks.append(
                    {
                        "block_type": 27,
                        "table": {"property": {}, "cells": []},
                    }
                )
            elif line.strip():
                blocks.append(
                    {
                        "block_type": 2,
                        "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}},
                    }
                )
        return blocks

    def update_document(self, doc_id: str, content: str) -> FeishuDocument:
        """更新文档内容"""
        self._add_document_content(doc_id, content)
        return self.get_document(doc_id)

    def add_comment(
        self, doc_id: str, content: str, position: Optional[Dict] = None
    ) -> str:
        """添加文档评论"""
        endpoint = f"/drive/v1/files/{doc_id}/comments"
        payload: Dict[str, Any] = {"content": content}
        if position:
            payload["position"] = position

        response = self._request("POST", endpoint, json=payload)
        return response["data"]["comment_id"]

    def get_document(self, doc_id: str) -> FeishuDocument:
        """获取文档信息"""
        endpoint = f"/docx/v1/documents/{doc_id}"
        response = self._request("GET", endpoint)
        doc = response["data"]["document"]

        return FeishuDocument(
            doc_id=doc["document_id"],
            title=doc["title"],
            url=f"https://xxx.feishu.cn/docx/{doc_id}",
            version=doc.get("revision", 1),
            created_time=doc["create_time"],
            modified_time=doc["modify_time"],
        )