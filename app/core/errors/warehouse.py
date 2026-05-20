#WarehouseErrors

class WarehouseCapacityError(Exception):
    """Исключение, возникающее если новая вместимость меньше старой вместимости"""

    def __init__(self, message: str | Exception = "Новая вместимость ячеек меньше старой") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message