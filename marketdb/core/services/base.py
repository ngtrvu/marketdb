class BaseService:
    data = None
    error_message = None

    def is_valid(self) -> bool:
        raise NotImplementedError("please override this")

    def get_error_message(self) -> str:
        return self.error_message

    def get_data(self):
        return self.data

    def call(self) -> bool:
        pass
