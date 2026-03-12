# Frontend (Nuxt 3)

Mục tiêu: triển khai UI theo `figma_redesign/`.

## Thư mục chính
- `assets/styles/`: tokens + theme
- `components/ui/`: các component cơ bản (Button, Input, Table...)
- `components/blocks/`: khối màn hình (cards, charts, chat box)
- `layouts/`: layout Admin/User/Auth
- `pages/`: routing theo role
- `services/api/`: client gọi backend
- `stores/`: pinia stores

## Gợi ý pages (sẽ triển khai)
- `/login`, `/forgot-password`, `/reset-password`
- `/admin/overview`, `/admin/query`, `/admin/import`, `/admin/import/validate`, `/admin/import/detail`, `/admin/data`, `/admin/users`, `/admin/users/:id`, `/admin/logs`, `/admin/settings`
- `/user/overview`, `/user/query`, `/user/history`, `/user/history/:id`
