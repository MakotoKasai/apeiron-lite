# プロジェクト：操作の失敗を表す業務例外。


class ProjectAlreadyExistsError(Exception):
    pass
class ProjectDoesNotExistsError(Exception):
    pass
class InvalidProjectInputError(Exception):
    pass