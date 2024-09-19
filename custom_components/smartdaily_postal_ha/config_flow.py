import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import requests
import aiohttp

DOMAIN = "smartdaily_postal_ha"
KingnetAuthValue = ""


class MyParcelTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """smartdaily_postal_ha config flow."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self.device_id = user_input["DeviceID"]  # 获取DeviceID的值
            url = (
                "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code="
                + self.device_id
            )
            headers = {
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*"
            }
            response = await self.hass.async_add_executor_job(
                requests.get, url, headers
            )
            if response.status_code == 200:
                print("Success!\nResult:\n")
                print(response.text)
                print("\n------Beautify------\n")
                # 解析JSON數據
                data = response.json()

                self.KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
                print(KingnetAuthValue)
            else:
                print("請求失敗，狀態碼:", response.status_code)
            # 尝试使用DeviceID获取KingnetAuth令牌和社区列表
            # 这里需要添加逻辑来调用API
            # ...

            # 假设成功，转到社区选择步骤
            return await self.async_step_select_community()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("DeviceID"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_community(self, user_input=None):
        """Handle the step to select a community."""
        errors = {}
        if user_input is not None:
            # 用户已选择社区，存储选定的社区ID并创建配置条目
            return self.async_create_entry(
                title="My Parcel Tracker",
                data={"DeviceID": self.device_id, "com_id": user_input["com_id"]},
            )

        # 获取社区列表并生成选项
        communities = await self._get_communities(self.KingnetAuthValue)
        options = {com["id"]: com["community"] for com in communities}

        return self.async_show_form(
            step_id="select_community",
            data_schema=vol.Schema(
                {
                    vol.Required("com_id", description="選擇社區"): vol.In(options),
                }
            ),
            errors=errors,
        )

    async def _get_communities(self, KingnetAuthValue):
        """获取社区列表。"""
        headers = {
            "Connection": "keep-alive",
            "KingnetAuth": self.KingnetAuthValue,
            "Accept": "application/json, text/plain, */*"
        }
        communities = []  # 初始化空列表用于存储社区信息
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.smartdaily.com.tw/api/Community/GetUserCommunityList",
                headers=headers,
            ) as response:
                print("-----------")
                print(headers)
                if response.status == 200:
                    data = await response.json()  # 使用await等待异步操作完成
                    for com in data["Data"]:
                        # 将每个社区的信息添加到列表中
                        communities.append(
                            {"id": com["id"], "community": com["community"]}
                        )
                else:
                    print("请求失败，状态码:", response.status)
                    text = await response.text()  # 使用await获取响应文本
                    print(text)
                    # 可以考虑抛出异常或进行其他错误处理

        return communities
