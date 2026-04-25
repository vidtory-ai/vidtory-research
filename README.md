# Vidtory AI Research

Public research, reverse-engineering notes, and technical analysis by [Vidtory AI](https://github.com/vidtory-ai).

---

## 📚 Research Index

| # | Date | Topic | Description |
|---|------|-------|-------------|
| 1 | 2026-04-25 | [Codex ImageGen Skill](./research/2026-04-25-codex-imagegen-skill/) | Phân tích cơ chế hoạt động của skill sinh ảnh `imagegen` trong OpenAI Codex — built-in tool vs CLI fallback, prompt schema, transparent image workflow, model matrix |

---

## Cấu trúc thư mục

```
vidtory-research/
├── README.md                           ← File này (master index)
└── research/
    └── YYYY-MM-DD-topic-name/          ← Mỗi research 1 folder
        ├── README.md                   ← Tổng quan research
        └── ...                         ← Tài liệu, code, assets
```

## Quy ước đặt tên

- **Folder**: `YYYY-MM-DD-kebab-case-topic` — sắp xếp theo thời gian tự nhiên
- **README.md** trong mỗi folder: tổng quan, cách hoạt động, kết luận
- File bổ sung: spec, code, scripts, assets đi kèm

## License

Mỗi research có thể có license riêng. Xem file `LICENSE.txt` trong từng folder.
