# Image Gen Built-in Tool — API Specification

Tài liệu này trích xuất **toàn bộ cấu trúc request / response** của công cụ nội bộ `image_gen` (built-in tool) trong hệ thống Codex, dựa trên phân tích ngược từ skill `imagegen`.

---

## 1. Tổng quan kiến trúc

```
┌────────────────────────────────┐
│        User (Codex Chat)       │
│  "Tạo một ảnh hero cho web"   │
└──────────────┬─────────────────┘
               │  prompt (text)
               ▼
┌────────────────────────────────┐
│     Codex Agent (LLM Core)     │
│  - Phân loại intent            │
│  - Augment prompt theo spec    │
│  - Gọi built-in image_gen     │
└──────────────┬─────────────────┘
               │  internal tool call
               ▼
┌────────────────────────────────┐
│   Built-in image_gen Tool      │
│  (Native, server-side proxy)   │
│  - Không cần OPENAI_API_KEY    │
│  - Không expose CLI flags      │
│  - Output → $CODEX_HOME/       │
│      generated_images/...      │
└──────────────┬─────────────────┘
               │  image file(s)
               ▼
┌────────────────────────────────┐
│   Post-processing (optional)   │
│  - Chroma-key removal (PNG)    │
│  - Move/Copy to workspace      │
└────────────────────────────────┘
```

---

## 2. Built-in `image_gen` — Input Parameters

Công cụ built-in `image_gen` **KHÔNG** expose các tham số CLI như `--quality`, `--size`, `--background`, `--input-fidelity`, `--output-format`. Những thứ đó chỉ có ở Fallback CLI mode.

### Tham số duy nhất mà built-in tool nhận:

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `Prompt` | `string` | ✅ | Mô tả nội dung ảnh cần sinh. Agent sẽ augment prompt theo schema trước khi truyền vào. |
| `ImageName` | `string` | ✅ | Tên file output (lowercase, underscore, tối đa 3 từ). VD: `hero_page_mockup` |
| `ImagePaths` | `string[]` | ❌ | Đường dẫn tuyệt đối đến các ảnh đầu vào (tối đa 3 file). Dùng khi edit hoặc cần reference. |

> **Lưu ý quan trọng:** Built-in tool không có tham số `size`, `quality`, `background`, `output_format`, `n`, `model`, `mask`, `input_fidelity`. Tất cả những tham số này **chỉ** tồn tại trong Fallback CLI mode (`scripts/image_gen.py`).

---

## 3. Built-in `image_gen` — Output

| Thuộc tính | Mô tả |
|------------|-------|
| Đường dẫn lưu | `$CODEX_HOME/generated_images/...` (mặc định `~/.codex/generated_images/`) |
| Định dạng | Bitmap (PNG hoặc tương đương), do hệ thống quyết định |
| Preview | Ảnh được render inline trong conversation context |
| Số lượng | 1 ảnh / 1 lần gọi tool. Muốn nhiều biến thể → gọi nhiều lần. |

---

## 4. Prompt Schema (Cấu trúc prompt gửi vào tool)

Agent sẽ **augment** prompt của người dùng thành cấu trúc spec sau trước khi gửi vào `image_gen`:

```text
Use case: <taxonomy slug>
Asset type: <nơi ảnh sẽ được sử dụng>
Primary request: <yêu cầu chính của người dùng>
Input images: <Image 1: role; Image 2: role> (nếu có)
Scene/backdrop: <bối cảnh / môi trường>
Subject: <chủ thể chính>
Style/medium: <photo / illustration / 3D / etc>
Composition/framing: <wide / close / top-down; vị trí>
Lighting/mood: <ánh sáng + tâm trạng>
Color palette: <ghi chú bảng màu>
Materials/textures: <chi tiết bề mặt>
Text (verbatim): "<văn bản chính xác>"
Constraints: <phải giữ / phải tránh>
Avoid: <ràng buộc phủ định>
```

### Các Use-case taxonomy slugs:

#### Nhóm Generate:
| Slug | Mô tả |
|------|-------|
| `photorealistic-natural` | Ảnh chụp candid/editorial với texture và ánh sáng tự nhiên |
| `product-mockup` | Ảnh sản phẩm / bao bì / catalog |
| `ui-mockup` | Mockup giao diện app/web |
| `infographic-diagram` | Biểu đồ / infographic có cấu trúc |
| `scientific-educational` | Sơ đồ khoa học, giáo dục |
| `ads-marketing` | Creative quảng cáo / chiến dịch |
| `productivity-visual` | Slide, chart, workflow, biểu đồ dữ liệu |
| `logo-brand` | Logo / brand mark |
| `illustration-story` | Minh họa truyện / comic |
| `stylized-concept` | Concept art phong cách hóa / 3D render |
| `historical-scene` | Cảnh lịch sử chính xác theo thời kỳ |

#### Nhóm Edit:
| Slug | Mô tả |
|------|-------|
| `text-localization` | Thay đổi / dịch text trong ảnh |
| `identity-preserve` | Thử đồ, giữ nguyên nhận dạng người |
| `precise-object-edit` | Xóa / thay thế vật thể cụ thể |
| `lighting-weather` | Thay đổi thời tiết / ánh sáng |
| `background-extraction` | Tách nền / transparent background |
| `style-transfer` | Áp dụng phong cách từ reference |
| `compositing` | Ghép nhiều ảnh với ánh sáng khớp |
| `sketch-to-render` | Chuyển bản vẽ thành ảnh thực |

---

## 5. Decision Tree (Luồng quyết định)

```
User request
  │
  ├── Có muốn sửa ảnh có sẵn? ──── YES ──→ Intent = EDIT
  │                                           │
  │                                           ├── Ảnh đã có trong context? → Dùng built-in edit
  │                                           └── Ảnh chỉ ở filesystem? → view_image trước → built-in edit
  │
  └── Không / Ảnh chỉ là reference ──→ Intent = GENERATE
                                         │
                                         ├── Cần transparent? ──→ Chroma-key workflow
                                         │                        (sinh ảnh nền #00ff00 → remove_chroma_key.py)
                                         │
                                         ├── Nhiều assets? ──→ Gọi image_gen nhiều lần (1 call / 1 asset)
                                         │
                                         └── Single asset ──→ 1 lần gọi image_gen
```

---

## 6. Transparent Image Workflow (Chi tiết)

Đây là workflow đặc biệt của skill khi user yêu cầu ảnh nền trong suốt mà **vẫn dùng built-in tool**:

### Bước 1: Sinh ảnh với Chroma-key background
Prompt sẽ được augment thêm đoạn này:
```text
Create the requested subject on a perfectly flat solid #00ff00 chroma-key background
for background removal.
The background must be one uniform color with no shadows, gradients, texture,
reflections, floor plane, or lighting variation.
Keep the subject fully separated from the background with crisp edges and generous padding.
Do not use #00ff00 anywhere in the subject.
No cast shadow, no contact shadow, no reflection, no watermark, and no text unless
explicitly requested.
```

### Bước 2: Copy ảnh ra workspace
```bash
# Ảnh nằm tại ~/.codex/generated_images/...
# → Copy sang workspace hoặc tmp/imagegen/
```

### Bước 3: Chạy script xóa nền
```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input <source.png> \
  --out <final.png> \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

### Bước 4: Validate
- Kiểm tra ảnh output có kênh alpha
- Kiểm tra corners trong suốt
- Kiểm tra subject coverage hợp lý
- Nếu còn fringe → retry với `--edge-contract 1`

### Chọn key color:
| Tình huống | Key color |
|-----------|-----------|
| Mặc định | `#00ff00` (xanh lá) |
| Chủ thể có màu xanh lá | `#ff00ff` (magenta) |
| Chủ thể có màu xanh dương | Tránh `#0000ff` |

---

## 7. `remove_chroma_key.py` — Tham số đầy đủ

| Tham số | Kiểu | Default | Mô tả |
|---------|------|---------|-------|
| `--input` | string | _(bắt buộc)_ | Đường dẫn ảnh đầu vào |
| `--out` | string | _(bắt buộc)_ | Đường dẫn output (.png hoặc .webp) |
| `--key-color` | hex | `#00ff00` | Màu key cần xóa |
| `--tolerance` | int | `12` | Hard-key tolerance mỗi kênh (0-255) |
| `--auto-key` | `none`\|`corners`\|`border` | `none` | Tự sample key color từ viền ảnh |
| `--soft-matte` | flag | `false` | Dùng alpha ramp mượt |
| `--transparent-threshold` | float | `12.0` | Khoảng cách ≤ giá trị này → fully transparent |
| `--opaque-threshold` | float | `96.0` | Khoảng cách ≥ giá trị này → fully opaque |
| `--edge-feather` | float | `0.0` | Blur radius cho cạnh mềm (0-64) |
| `--edge-contract` | int | `0` | Thu nhỏ alpha matte N pixel trước feather (0-16) |
| `--spill-cleanup` / `--despill` | flag | `false` | Giảm spill màu key trên pixel opaque |
| `--force` | flag | `false` | Ghi đè file output đã tồn tại |

---

## 8. Fallback CLI Mode — So sánh tham số

Khi user **chủ động yêu cầu** CLI mode, script `scripts/image_gen.py` expose bộ tham số đầy đủ hơn nhiều:

### Generate endpoint: `POST /v1/images/generations`

| Tham số | Kiểu | Default | Mô tả |
|---------|------|---------|-------|
| `--prompt` | string | _(bắt buộc)_ | Text prompt |
| `--prompt-file` | string | - | Đọc prompt từ file |
| `--model` | string | `gpt-image-2` | Model tạo ảnh |
| `--n` | int | `1` | Số lượng ảnh (1-10) |
| `--size` | string | `auto` | Kích thước output |
| `--quality` | `low`\|`medium`\|`high`\|`auto` | `medium` | Chất lượng |
| `--background` | `transparent`\|`opaque`\|`auto` | - | Hành vi nền output |
| `--output-format` | `png`\|`jpeg`\|`webp` | `png` | Định dạng output |
| `--output-compression` | int | - | Nén (0-100, chỉ jpeg/webp) |
| `--moderation` | `auto`\|`low` | `auto` | Mức kiểm duyệt |
| `--out` | string | `output/imagegen/output.png` | Đường dẫn output |
| `--out-dir` | string | - | Thư mục output |
| `--force` | flag | `false` | Ghi đè file đã tồn tại |
| `--dry-run` | flag | `false` | Chỉ in payload, không gọi API |
| `--downscale-max-dim` | int | - | Tạo thêm bản thu nhỏ |
| `--downscale-suffix` | string | `-web` | Hậu tố bản thu nhỏ |

### Prompt augmentation flags (CLI):
| Flag | Mô tả |
|------|-------|
| `--use-case` | Taxonomy slug |
| `--scene` | Bối cảnh |
| `--subject` | Chủ thể |
| `--style` | Phong cách |
| `--composition` | Bố cục |
| `--lighting` | Ánh sáng |
| `--palette` | Bảng màu |
| `--materials` | Chất liệu |
| `--text` | Văn bản verbatim |
| `--constraints` | Ràng buộc |
| `--negative` | Tránh / loại trừ |
| `--no-augment` | Tắt augmentation |

### Edit endpoint: `POST /v1/images/edits`
Thêm các tham số:

| Tham số | Mô tả |
|---------|-------|
| `--image` | Ảnh đầu vào (có thể lặp, tối đa 16 ảnh) |
| `--mask` | Ảnh mask (PNG có alpha channel) |
| `--input-fidelity` | `low`\|`high` (không dùng với gpt-image-2) |

### Batch endpoint: `generate-batch`
Thêm các tham số:

| Tham số | Default | Mô tả |
|---------|---------|-------|
| `--input` | _(bắt buộc)_ | File JSONL chứa danh sách job |
| `--concurrency` | `5` | Số job chạy song song (1-25) |
| `--max-attempts` | `3` | Số lần retry mỗi job (1-10) |
| `--fail-fast` | `false` | Dừng ngay nếu 1 job thất bại |

---

## 9. Model Support Matrix

| Model | Quality | Input fidelity | Sizes | Transparent | Ghi chú |
|-------|---------|----------------|-------|-------------|---------|
| `gpt-image-2` | `low` `medium` `high` `auto` | Luôn high (không set được) | Tùy biến: max 3840px, bội số 16px, ratio ≤ 3:1 | ❌ | Mặc định cho CLI |
| `gpt-image-1.5` | `low` `medium` `high` `auto` | `low` `high` | `1024²` `1024×1536` `1536×1024` `auto` | ✅ | Fallback cho transparent |
| `gpt-image-1` | `low` `medium` `high` `auto` | `low` `high` | `1024²` `1024×1536` `1536×1024` `auto` | ✅ | Legacy |
| `gpt-image-1-mini` | `low` `medium` `high` `auto` | `low` `high` | `1024²` `1024×1536` `1536×1024` `auto` | ✅ | Draft / low-cost |

### Kích thước phổ biến cho `gpt-image-2`:
| Label | Size | Ghi chú |
|-------|------|---------|
| Square | `1024x1024` | Nhanh nhất |
| Landscape | `1536x1024` | Standard landscape |
| Portrait | `1024x1536` | Standard portrait |
| 2K square | `2048x2048` | Lớn hơn |
| 2K landscape | `2048x1152` | Widescreen |
| 4K landscape | `3840x2160` | Widescreen 4K |
| 4K portrait | `2160x3840` | Vertical 4K |
| Auto | `auto` | Để hệ thống tự chọn |

---

## 10. File Structure Map

```
imagegen-skill/
├── SKILL.md                           # Tài liệu gốc, luật & workflow
├── LICENSE.txt                        # License
├── README.md                          # Mô tả tổng quan (file này)
├── IMAGE_GEN_API_SPEC.md              # ← BẠN ĐANG ĐỌC FILE NÀY
│
├── agents/
│   └── openai.yaml                    # Agent config (display name, icon)
│
├── assets/
│   ├── imagegen-small.svg             # Icon nhỏ
│   └── imagegen.png                   # Icon lớn
│
├── references/
│   ├── prompting.md                   # Nguyên tắc viết prompt (shared)
│   ├── sample-prompts.md              # Bộ prompt mẫu copy/paste (shared)
│   ├── cli.md                         # CLI reference (fallback only)
│   ├── image-api.md                   # API parameter reference (fallback only)
│   └── codex-network.md              # Network / sandbox config (fallback only)
│
└── scripts/
    ├── image_gen.py                   # CLI fallback implementation (996 lines)
    └── remove_chroma_key.py           # Chroma-key → alpha converter (441 lines)
```

---

## 11. Ví dụ Request thực tế

### Built-in tool call (dạng nội bộ agent gọi):
```json
{
  "tool": "image_gen",
  "arguments": {
    "Prompt": "Use case: product-mockup\nAsset type: landing page hero\nPrimary request: a minimal hero image of a ceramic coffee mug\nStyle/medium: clean product photography\nComposition/framing: wide composition with usable negative space for page copy if needed\nLighting/mood: soft studio lighting\nConstraints: no logos, no text, no watermark",
    "ImageName": "ceramic_mug_hero"
  }
}
```

### CLI fallback generate (dạng terminal):
```bash
python "$IMAGE_GEN" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --quality medium \
  --out output/imagegen/alpine-cabin.png
```

### CLI fallback edit (dạng terminal):
```bash
python "$IMAGE_GEN" edit \
  --image input.png \
  --prompt "Replace only the background with a warm sunset" \
  --quality high \
  --out output/imagegen/sunset-edit.png
```

### CLI batch (dạng JSONL + terminal):
```jsonl
{"prompt":"Cavernous hangar interior","use_case":"stylized-concept","size":"1536x1024"}
{"prompt":"Gray wolf in snowy forest","use_case":"photorealistic-natural","size":"1024x1024"}
```
```bash
python "$IMAGE_GEN" generate-batch \
  --input tmp/imagegen/prompts.jsonl \
  --out-dir output/imagegen/batch \
  --concurrency 5
```
