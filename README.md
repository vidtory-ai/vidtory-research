# Vidtory AI Research

> Tổng hợp các nghiên cứu kỹ thuật được thực hiện trong quá trình xây dựng **[Vidtory AI](https://github.com/vidtory-ai)** — nền tảng sáng tạo nội dung hình ảnh và video bằng AI.

Repo này lưu trữ và chia sẻ công khai những phân tích, reverse-engineering, và tài liệu kỹ thuật mà đội ngũ Vidtory AI tích lũy được khi làm việc với các nền tảng AI generative hàng đầu. Mục tiêu là giúp cộng đồng developer và creator **nhanh chóng nắm bắt, tận dụng và tối ưu** các công cụ, API, và kiến trúc mới nhất trong lĩnh vực AI tạo ảnh/video — thay vì phải tự mò mẫm từ đầu.

---

## 🔬 Research Index

| # | Ngày | Chủ đề | Mô tả |
|---|------|--------|-------|
| 1 | 2026-04-25 | [Codex ImageGen Skill](./research/2026-04-25-codex-imagegen-skill/) | Phân tích toàn bộ cơ chế hoạt động của skill sinh ảnh `imagegen` trong OpenAI Codex — built-in tool API spec, prompt schema, transparent image workflow (chroma-key hack), model matrix, CLI fallback |

---

## 🎯 Mục tiêu

- **Giải mã nhanh** cách các nền tảng AI (OpenAI, Google, Runway, Kling...) tổ chức pipeline tạo ảnh/video
- **Trích xuất API spec** và cấu trúc request thực tế để tích hợp vào sản phẩm
- **Chia sẻ best practices** về prompt engineering, workflow tối ưu, và các trick kỹ thuật
- **Ghi chép kiến trúc** các hệ thống AI generative đang thay đổi nhanh chóng

## 📂 Cấu trúc

```
vidtory-research/
├── README.md                           ← Danh mục tổng hợp (file này)
└── research/
    └── YYYY-MM-DD-topic-name/          ← Mỗi nghiên cứu là 1 folder
        ├── README.md                   ← Tổng quan & kết luận
        └── ...                         ← Tài liệu chi tiết, code, assets
```

Mỗi folder nghiên cứu chứa đầy đủ context để đọc độc lập — không cần đọc các research khác.

## 🤝 Đóng góp

Nếu bạn phát hiện thông tin lỗi thời hoặc muốn bổ sung research mới, hãy mở issue hoặc pull request. Các nền tảng AI thay đổi rất nhanh — mọi đóng góp cập nhật đều có giá trị.

## 📜 License

Mỗi research có thể có license riêng phù hợp với nguồn gốc tài liệu. Xem file `LICENSE.txt` trong từng folder cụ thể.

---

**Vidtory AI** · [GitHub](https://github.com/vidtory-ai)
