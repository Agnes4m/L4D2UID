from typing import Optional

from gsuid_core.utils.database.startup import exec_list
from gsuid_core.utils.database.base_models import Bind, User, with_session
from gsuid_core.webconsole.mount_app import GsAdminModel, PageSchema, site
from sqlmodel import Field

exec_list.extend(
    [
        'ALTER TABLE L4D2Bind ADD COLUMN steam32 TEXT DEFAULT ""',
        'ALTER TABLE L4D2Bind ADD COLUMN searchtype TEXT DEFAULT "云"',
    ]
)

class L4D2Bind(Bind, table=True):
    __table_args__ = {'extend_existing': True}
    uid: Optional[str] = Field(default=None, title="L4D2UID")
    steam32: Optional[str] = Field(default="", title="steam64")
    searchtype: str = Field(default="云", title="搜索类型")

    @classmethod
    @with_session
    async def switch_steam32(
        cls,
        session,
        user_id: str,
        bot_id,
        steam32: str,
    ) -> int:
        """更改steam32的参数值"""
        try:
            data = await cls.insert_data(user_id, bot_id, steam32=steam32)
        except Exception as e:
            # logger.error(e)
            data = await cls.update_data(user_id, bot_id, steam32=steam32)
        return data

    @classmethod
    @with_session
    async def get_steam32(
        cls,
        session,
        user_id: str,
    ):
        """获取steam32的参数值"""
        data = await cls.select_data(user_id)

        return data.steam32 if data else None

    @classmethod
    @with_session
    async def switch_searchtype(
        cls,
        session,
        user_id: str,
        bot_id,
        searchtype: str,
    ) -> int:
        """更改steam32的参数值"""

        data = await cls.update_data(user_id, bot_id, searchtype=searchtype)
        return data

    @classmethod
    @with_session
    async def get_searchtype(
        cls,
        session,
        user_id: str,
    ):
        """获取searchtype的参数值"""
        data = await cls.select_data(user_id)

        return data.searchtype if data else None

class L4D2User(User, table=True):
    __table_args__ = {'extend_existing': True}
    uid: Optional[str] = Field(default=None, title="L4D2UID")


@site.register_admin
class L4D2Bindadmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="L4D2绑定管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = L4D2Bind


@site.register_admin
class L4D2Useradmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="L4D2用户管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = L4D2User
