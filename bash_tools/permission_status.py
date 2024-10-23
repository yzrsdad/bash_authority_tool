from enum import Enum

class PermissionStatus(Enum):
    READ_OUT_OF_BOUNDS = False
    WRITE_OUT_OF_BOUNDS = False
    EXECUTE_OUT_OF_BOUNDS = False
    NOT_SUPERUSER = False
    NOT_OWNER = False
    NO_OUT_OF_BOUNDS = True


    def description(self):
        """
        返回枚举项的中文描述
        """
        if self == PermissionStatus.READ_OUT_OF_BOUNDS:
            return "读取权限超出范围"
        elif self == PermissionStatus.WRITE_OUT_OF_BOUNDS:
            return "写入权限超出范围"
        elif self == PermissionStatus.EXECUTE_OUT_OF_BOUNDS:
            return "执行权限超出范围"
        elif self == PermissionStatus.NOT_SUPERUSER:
            return "不是超级用户"
        elif self == PermissionStatus.NOT_OWNER:
            return "不是所有者"
        elif self == PermissionStatus.NO_OUT_OF_BOUNDS:
            return "没有权限超出"



    def __str__(self):
        """
        返回枚举项的字符串表示形式
        """
        return self.name
