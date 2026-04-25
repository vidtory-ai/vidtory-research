# Codex Image Generation Skill (`imagegen`)

Skill sinh tạo & chỉnh sửa ảnh bitmap/raster tích hợp trong hệ thống Codex. Hỗ trợ tạo ảnh mockup, banner, concept art, product shot, UI wireframe, logo, ảnh trong suốt và nhiều loại tài sản hình ảnh khác.

---

## Cách hoạt động

Skill có **2 chế độ (mode)** chạy song song:

### 1. Built-in Tool Mode (Mặc định & Ưu tiên)

- Sử dụng công cụ nội bộ `image_gen` của hệ thống Codex.
- **Không cần `OPENAI_API_KEY`** — xác thực được xử lý nội bộ qua hạ tầng backend.
- Ảnh sinh ra được lưu vào `~/.codex/generated_images/` rồi copy sang workspace khi cần.
- Chỉ nhận 2-3 tham số: `Prompt`, `ImageName`, và `ImagePaths` (tùy chọn).
- Không expose các tham số nâng cao như `size`, `quality`, `background`, `model`.

### 2. Fallback CLI Mode (Khi được yêu cầu)

- Sử dụng script `scripts/image_gen.py` gọi trực tiếp OpenAI Image API.
- **Bắt buộc có `OPENAI_API_KEY`**.
- Hỗ trợ đầy đủ 3 lệnh: `generate`, `edit`, `generate-batch`.
- Expose toàn bộ tham số: `model`, `size`, `quality`, `background`, `output-format`, `mask`, `input-fidelity`, v.v.
- Mặc định dùng model `gpt-image-2`.

---

## Tính năng đặc biệt

### Xử lý ảnh nền trong suốt (Transparency Hack)

Vì built-in tool không hỗ trợ trực tiếp transparent background, skill áp dụng chiến thuật **chroma-key**:

1. **Sinh ảnh** với phông nền xanh lá `#00ff00` (hoặc `#ff00ff` cho chủ thể màu xanh).
2. **Tải về local** và chạy script `remove_chroma_key.py` để tách nền → PNG có alpha channel.
3. **Validate** chất lượng cắt (kiểm tra corners, fringe, subject coverage).
4. Nếu thất bại → đề xuất chuyển sang CLI mode `gpt-image-1.5` (sau khi hỏi user).

### Prompt Augmentation (Làm giàu prompt)

Skill tự động cấu trúc lại prompt người dùng thành spec chuyên nghiệp với các trường:
- `Use case` → phân loại theo taxonomy (photorealistic, product-mockup, ui-mockup, ...)
- `Scene/backdrop` → bối cảnh
- `Subject` → chủ thể
- `Style/medium` → phong cách
- `Composition/framing` → bố cục, khung hình
- `Lighting/mood` → ánh sáng
- `Constraints / Avoid` → ràng buộc & loại trừ

---

## Tài liệu chi tiết

| File | Nội dung |
|------|----------|
| [`IMAGE_GEN_API_SPEC.md`](./IMAGE_GEN_API_SPEC.md) | **Toàn bộ cấu trúc request/response** của built-in tool vs CLI, prompt schema, decision tree, model matrix, ví dụ thực tế |
| [`SKILL.md`](./SKILL.md) | Tài liệu gốc: luật, workflow, quy tắc vận hành skill |
| [`references/prompting.md`](./references/prompting.md) | Nguyên tắc viết prompt (shared cả 2 mode) |
| [`references/sample-prompts.md`](./references/sample-prompts.md) | Bộ prompt mẫu copy/paste |
| [`references/cli.md`](./references/cli.md) | CLI reference (fallback mode only) |
| [`references/image-api.md`](./references/image-api.md) | API parameter reference (fallback mode only) |
| [`references/codex-network.md`](./references/codex-network.md) | Network/sandbox troubleshooting |

---

## Cấu trúc thư mục

```
imagegen-skill/
├── SKILL.md                        # Tài liệu gốc, luật & workflow
├── IMAGE_GEN_API_SPEC.md           # Trích xuất API spec đầy đủ
├── README.md                       # ← File này
├── LICENSE.txt
├── agents/
│   └── openai.yaml                 # Agent config (display name, icon)
├── assets/
│   ├── imagegen-small.svg          # Icon nhỏ
│   └── imagegen.png                # Icon lớn
├── references/                     # Tài liệu tham khảo
│   ├── prompting.md
│   ├── sample-prompts.md
│   ├── cli.md
│   ├── image-api.md
│   └── codex-network.md
└── scripts/                        # Scripts thực thi
    ├── image_gen.py                # CLI fallback (996 dòng)
    └── remove_chroma_key.py        # Chroma-key → alpha (441 dòng)
```

---

## Có thể dùng ChatGPT OAuth để gọi trực tiếp không?

**KHÔNG.** Skill này hoạt động theo 2 cách:

1. **Built-in mode**: Xác thực qua hạ tầng nội bộ Codex (server-side proxy), không cần key gì cả, nhưng chỉ hoạt động bên trong môi trường Codex agent.
2. **CLI mode**: Yêu cầu `OPENAI_API_KEY` (developer API key dạng `sk-...`), không hỗ trợ OAuth authentication flow.

ChatGPT OAuth token (dạng login web account) không tương thích với cả hai cơ chế trên.
