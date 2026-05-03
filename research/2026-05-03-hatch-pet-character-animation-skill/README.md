# Hatch Pet -> Character Sheet Animator

Research này lưu lại toàn bộ skill `hatch-pet` hiện có và rewrite nó thành một skill tổng quát hơn: tạo **character sheet** và **animation sheet** cho mọi nhân vật bất kỳ.

Mục tiêu không phải tạo một Codex pet mới, mà tách phần pipeline tốt của `hatch-pet` ra khỏi ràng buộc pet-specific để dùng cho nhân vật trong game, video, comic, mascot, avatar, IP character, AI video reference, sprite sheet, hoặc bất kỳ workflow thiết kế nhân vật nào.

---

## Kết quả chính

| Hạng mục | File |
| --- | --- |
| Skill đã rewrite | [`SKILL.md`](./SKILL.md) |
| Toàn bộ source `hatch-pet` gốc | [`source/hatch-pet/`](./source/hatch-pet/) |
| Danh sách source đã copy | [`SOURCE_INVENTORY.md`](./SOURCE_INVENTORY.md) |
| Scripts tổng quát cho skill mới | [`scripts/`](./scripts/) |
| Contract output mới | [`references/sheet-contracts.md`](./references/sheet-contracts.md) |
| Prompt template mới | [`references/prompt-patterns.md`](./references/prompt-patterns.md) |
| QA rubric mới | [`references/qa-rubric.md`](./references/qa-rubric.md) |
| Ghi chú migration | [`references/migration-from-hatch-pet.md`](./references/migration-from-hatch-pet.md) |
| UI metadata skill | [`agents/openai.yaml`](./agents/openai.yaml) |
| Demo chạy thử với Vidtory mascot | [`runs/vidtory-spark-demo/`](./runs/vidtory-spark-demo/) |

---

## Thay đổi tư duy

`hatch-pet` rất mạnh ở các điểm:

- tạo canonical base trước khi tạo pose/row
- dùng `$imagegen` làm lớp sinh hình chính
- sinh row animation theo từng action thay vì một sheet quá lớn
- dùng layout guide cho frame count/spacing/cell geometry
- tách chroma-key thành alpha khi cần transparent sprite
- kiểm tra contact sheet, validation, identity drift
- repair theo phạm vi nhỏ nhất thay vì regenerate toàn bộ

Nhưng `hatch-pet` bị khóa vào runtime của Codex pet:

- atlas cố định `1536x1872`
- grid cố định `8x9`
- cell cố định `192x208`
- row state cố định cho pet
- output `pet.json`
- folder `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/`
- style mặc định là Codex digital pet

Skill mới giữ phần pipeline có giá trị và thay thế contract đầu ra bằng hệ thống linh hoạt:

- character sheet / model sheet
- turnaround sheet
- expression sheet
- outfit/prop variant sheet
- animation row strip
- sprite sheet / atlas nếu có target engine
- AI video consistency pack
- manifest JSON ghi prompt, source, geometry, QA

---

## Cấu trúc research

```text
2026-05-03-hatch-pet-character-animation-skill/
├── README.md
├── SKILL.md                         # bản rewrite: character-sheet-animator
├── SOURCE_INVENTORY.md              # xác nhận source hatch-pet đã copy đầy đủ
├── LICENSE.txt
├── agents/
│   └── openai.yaml
├── scripts/                         # script layer mới, đã đổi contract sang character sheet
│   ├── character_job_status.py
│   ├── finalize_character_run.py
│   ├── make_contact_sheet.py
│   ├── prepare_character_run.py
│   ├── queue_character_repairs.py
│   ├── record_imagegen_result.py
│   └── validate_character_run.py
├── references/
│   ├── migration-from-hatch-pet.md
│   ├── prompt-patterns.md
│   ├── qa-rubric.md
│   └── sheet-contracts.md
├── runs/
│   └── vidtory-spark-demo/          # output demo sau khi test skill với logo Vidtory
└── source/
    └── hatch-pet/                   # snapshot đầy đủ của skill gốc
        ├── SKILL.md
        ├── LICENSE.txt
        ├── agents/
        ├── references/
        └── scripts/
```

---

## Skill mới làm gì

`character-sheet-animator` được thiết kế để trigger khi người dùng muốn:

- "create character sheet"
- "make an animation sheet"
- "turn this character into sprite sheet"
- "create turnaround / model sheet"
- "make expression sheet"
- "generate consistent poses for this character"
- "create AI video reference plates"

Workflow chính:

1. Xác định character, reference, style, output target và geometry.
2. Tạo hoặc chọn canonical base.
3. Dùng canonical base để tạo character sheet.
4. Dùng canonical base để tạo animation rows hoặc sprite sheet.
5. Tách alpha / assemble atlas / tạo contact sheet nếu cần.
6. Viết manifest và QA notes.
7. Repair phạm vi nhỏ nhất nếu identity, geometry, alpha hoặc frame count lỗi.

---

## Scripts mới

Các script ở root `scripts/` là bản tổng quát hóa từ workflow `hatch-pet`, không phải bản pet-specific copy/paste:

| Script | Vai trò |
| --- | --- |
| [`prepare_character_run.py`](./scripts/prepare_character_run.py) | Tạo run folder, `request.json`, `generation-jobs.json`, prompts, layout guides |
| [`character_job_status.py`](./scripts/character_job_status.py) | Liệt kê job `$imagegen` ready/blocked |
| [`record_imagegen_result.py`](./scripts/record_imagegen_result.py) | Ghi nhận output được chọn, tạo `canonical-base.png`, cập nhật manifest |
| [`make_contact_sheet.py`](./scripts/make_contact_sheet.py) | Tạo contact sheet cho animation rows đã hoàn tất |
| [`validate_character_run.py`](./scripts/validate_character_run.py) | Kiểm tra deterministic: file, image metadata, frame geometry, alpha status |
| [`queue_character_repairs.py`](./scripts/queue_character_repairs.py) | Mở lại job lỗi để repair theo phạm vi nhỏ |
| [`finalize_character_run.py`](./scripts/finalize_character_run.py) | Chạy validation/contact sheet và viết `qa/run-summary.json` |

### Workflow CLI

1. Chuẩn bị run folder:

```bash
python scripts/prepare_character_run.py \
  --character-name "Mika" \
  --description "a brave child explorer with a yellow raincoat" \
  --output character-sheet,animation-sheet \
  --action idle:6:front:true:"breathing and blink" \
  --action walk:8:right:true:"clear walking cycle"
```

2. Xem job nào đã sẵn sàng để gọi `$imagegen`:

```bash
python scripts/character_job_status.py \
  --run-dir character-sheet-runs/mika-<timestamp>
```

3. Sau khi `$imagegen` sinh ảnh, record output gốc vào manifest:

```bash
python scripts/record_imagegen_result.py \
  --run-dir character-sheet-runs/mika-<timestamp> \
  --job-id base \
  --source "$HOME/.codex/generated_images/.../ig_*.png"
```

4. Với transparent asset, chạy chroma-key helper của `$imagegen`, rồi ghi `transparent_output_path` trong `generation-jobs.json` nếu muốn validator kiểm tra bản alpha thay vì file RGB gốc.

5. Validate/finalize:

```bash
python scripts/validate_character_run.py \
  --run-dir character-sheet-runs/mika-<timestamp>

python scripts/finalize_character_run.py \
  --run-dir character-sheet-runs/mika-<timestamp>
```

### Demo đã chạy

Folder [`runs/vidtory-spark-demo/`](./runs/vidtory-spark-demo/) là test thực tế sau khi thêm scripts:

- Canonical mascot: [`generated/base.png`](./runs/vidtory-spark-demo/generated/base.png)
- Character sheet: [`generated/character-sheet.png`](./runs/vidtory-spark-demo/generated/character-sheet.png)
- Combined sprite sheet: [`generated/sprite-sheet.png`](./runs/vidtory-spark-demo/generated/sprite-sheet.png)
- Transparent outputs: [`processed/`](./runs/vidtory-spark-demo/processed/)
- Manifest: [`manifest.json`](./runs/vidtory-spark-demo/manifest.json)
- QA summary: [`qa/run-summary.json`](./runs/vidtory-spark-demo/qa/run-summary.json)

Demo này chứng minh pipeline chạy được từ `prepare -> imagegen -> record -> alpha cleanup -> validate -> finalize`. Sprite sheet demo hiện là **combined visual sprite sheet**; để xuất engine-grade atlas thật, cần generate/record từng row riêng rồi thêm script pack atlas theo target runtime.

---

## Lưu ý implementation

Research này không cài đè skill `hatch-pet` đang nằm trong `~/.codex/skills/hatch-pet`. Bản rewrite nằm ở `SKILL.md` của research folder để review, copy, hoặc install thành skill riêng sau này.

Các scripts trong `source/hatch-pet/scripts/` vẫn còn pet-specific và được giữ làm snapshot gốc. Script layer mới ở `scripts/` đã đổi sang contract trung lập cho character sheet/animation sheet; phần atlas packing engine-specific vẫn cần mở rộng thêm nếu muốn xuất thẳng sang từng game engine.
