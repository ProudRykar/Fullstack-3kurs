# Тестирование

## Backend (Python + pytest)

```bash
# Установка зависимостей (однократно)
cd backend
pip install -r requirements.txt

# Запуск всех тестов
cd backend
poetry run pytest -v

# Запуск конкретного файла
poetry run pytest tests/test_product_service.py -v

# Запуск тестов по маркеру (если есть)
poetry run pytest -m "unit" -v
```

**Backend тесты** (7 файлов, 148 тестов):
| Файл | Тестов | Что тестирует |
|---|---|---|
| `tests/test_domain_models.py` | 53 | Product, Receipt, Inventory, Warehouse, Role, Permission, TokenClaims |
| `tests/test_product_dto.py` | 7 | ProductDTO, ProductCreateDTO, ProductListDTO |
| `tests/test_rbac_service.py` | 10 | RBACService (has_permission, get_role_permissions) |
| `tests/test_product_service.py` | 12 | ProductService CRUD, поиск, поиск по коду |
| `tests/test_receipt_service.py` | 16 | ReceiptService (create, add_item, confirm, cancel) |
| `tests/test_inventory_service.py` | 16 | InventoryService (create, scan, complete) |
| `tests/test_warehouse_service.py` | 34 | WarehouseService (CRUD, cells, auto_assign) |

**Примечания:**
- Backend использует `pytest` + `anyio` (не `pytest-asyncio`).
- Моки: `FakeConfig`, `FakeMongoGateway`, `FakeRepo` — в `tests/conftest.py`.

---

## Frontend (Vitest + Testing Library)

```bash
# Установка зависимостей (однократно)
cd frontend
npm install

# Однократный прогон тестов
cd frontend
npm test

# Watch mode (перезапуск при изменениях)
npm run test:watch
```

**Frontend тесты** (9 файлов, 82 теста):
| Файл | Тестов | Что тестирует |
|---|---|---|
| `src/utils/permissions.test.ts` | 13 | hasPermission для всех ролей и пермишенов |
| `src/services/api.test.ts` | 19 | Эндпоинты auth, user, product, warehouse, inventory, receipt |
| `src/context/AuthContext.test.tsx` | 6 | Загрузка, login, logout, error handling |
| `src/context/WarehouseContext.test.tsx` | 7 | Загрузка складов, выбор, сброс |
| `src/components/AppLayout.test.tsx` | 7 | Навигация, селектор склада, админ-панель, logout |
| `src/components/ConfirmModal.test.tsx` | 5 | Открытие, закрытие, confirm/cancel |
| `src/components/PrivateRoute.test.tsx` | 8 | Auth guard, role guard, loading, redirects |
| `src/pages/LoginPage.test.tsx` | 5 | Форма логина, отправка, ошибки |
| `src/pages/RegisterPage.test.tsx` | 8 | Форма регистрации, валидация, отправка |

**Особенности jsdom:**
- `<dialog>` API не реализован в jsdom — добавлен полифилл в `src/test/setup.ts`
- label/input без `htmlFor` не ассоциируются — тесты используют `getByRole('textbox')` и `querySelector`

---

## Запуск всех тестов сразу

```bash
# Из корня проекта
(cd backend && pytest -v) && (cd frontend && npm test)

# Или по отдельности:
echo "=== Backend ===" && cd backend && pytest -v && cd .. && echo "=== Frontend ===" && cd frontend && npm test
```
