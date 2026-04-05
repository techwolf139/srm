"""钉钉文档 API 客户端"""
import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DingTalkDocument:
    """钉钉文档对象"""
    doc_id: str
    title: str
    url: str
    version: int
    created_time: int
    modified_time: int


class DingTalkAPIError(Exception):
    """钉钉 API 错误"""
    pass


class DingTalkClient:
    """钉钉开放平台 API 客户端"""
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        app: Optional[str] = None,
        tenant_code: Optional[str] = None,
        base_url: str = "https://oapi.dingtalk.com",
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.app = app
        self.tenant_code = tenant_code
        self.base_url = base_url
        self._access_token: Optional[str] = None
        self._token_expire: int = 0

    def _get_access_token(self) -> str:
        """获取钉钉访问令牌"""
        if self._access_token and time.time() < self._token_expire:
            return self._access_token

        # 获取企业应用身份凭证
        url = f"{self.base_url}/v1.0/oauth2/accessToken"
        params = {
            "appKey": self.app_key,
            "appSecret": self.app_secret,
        }
        
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("code") != 0:
            raise DingTalkAPIError(f"获取 AccessToken 失败：{data}")

        self._access_token = data["result"]["access_token"]
        self._token_expire = time.time() + data["result"]["expire_in"] - 300
        return self._access_token

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送钉钉 API 请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        headers["Content-Type"] = "application/json"

        response = requests.request(method, url, headers=headers, **kwargs)
        data = response.json()

        if data.get("code") != 0:
            raise DingTalkAPIError(f"API 调用失败：{data}")

        return data

    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """验证响应是否成功"""
        return data.get("code") == 0

    def create_document(
        self, 
        title: str, 
        content: str,
        share_scope: str = "PRIVATE",
    ) -> DingTalkDocument:
        """创建钉钉文档"""
        endpoint = "/doc/v1/documents"
        
        payload = {
            "title": title,
            "content": content,
            "shareMode": share_scope,
        }

        response = self._request("POST", endpoint, json=payload)
        doc_data = response["data"]

        return DingTalkDocument(
            doc_id=doc_data["docId"],
            title=title,
            url=f"https://www.dingtalk.com/s/doc/{doc_data['docId']}",
            version=int(doc_data.get("version", 1)),
            created_time=doc_data.get("createTime", 0),
            modified_time=0,
        )

    def update_document(self, doc_id: str, content: str) -> DingTalkDocument:
        """更新文档内容"""
        endpoint = f"/doc/v1/documents/{doc_id}"
        
        payload = {
            "content": content,
        }

        response = self._request("PATCH", endpoint, json=payload)
        doc_data = response["data"]

        return DingTalkDocument(
            doc_id=doc_id,
            title=doc_data["title"],
            url=f"https://www.dingtalk.com/s/doc/{doc_id}",
            version=int(doc_data["version"]),
            created_time=doc_data["createTime"],
            modified_time=doc_data["updateTime"],
        )

    def get_document(self, doc_id: str) -> DingTalkDocument:
        """获取文档信息"""
        endpoint = f"/doc/v1/documents/{doc_id}"
        
        response = self._request("GET", endpoint)
        doc_data = response["data"]

        return DingTalkDocument(
            doc_id=doc_data["docId"],
            title=doc_data["title"],
            url=f"https://www.dingtalk.com/s/doc/{doc_data['docId']}",
            version=int(doc_data["version"]),
            created_time=doc_data["createTime"],
            modified_time=doc_data["updateTime"],
        )

    def add_comment(
        self, 
        doc_id: str, 
        content: str,
        position: Optional[Dict] = None,
    ) -> str:
        """添加文档评论"""
        endpoint = f"/doc/v1/documents/{doc_id}/comments"
        
        payload = {
            "content": content,
        }
        if position:
            payload["position"] = position

        response = self._request("POST", endpoint, json=payload)
        return response["data"]["commentId"]