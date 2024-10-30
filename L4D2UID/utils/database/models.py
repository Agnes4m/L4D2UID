from typing import Optional

from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.webconsole.mount_app import GsAdminModel, PageSchema, site
from sqlmodel import Field


class L4D2Bind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title="L4D2UID")


class L4D2User(User, table=True):
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
