# KÉT Sans 1.0 — v1.0.0

Phát hành ngày 21-10-2026. Version nội bộ OpenType: **1.000**.

## Nội dung

- Bốn độ đậm: Light 300, Regular 400, Medium 500 và Bold 700; Medium tiếp tục phục vụ cả 500–600 trên web.
- 419 codepoint, bao gồm GF Latin Core, tiếng Việt và ký hiệu ₫.
- Font tĩnh OTF, TTF có hint và WOFF2; thêm bốn font Optical ở định dạng TTF/WOFF2.
- Optical có trục `opsz` 8–72, mặc định 16. Giữ nhịp Text qua opsz 16, thu spacing dần tới Display ở 48; không bóp ngang hay thay nét glyph.
- Bật `font-optical-sizing: auto` khi dùng Optical. Không cần tracking âm toàn cục. Ánh xạ cỡ CSS sang opsz do trình duyệt quyết định.

Gói `KETSans-1.000.zip` có 20 file font, LICENSE và README. Tải file ZIP trong Assets;
source archive tự động của GitHub là source dự án, không phải gói cài font.
Giấy phép KÉT Sans Font License 1.0 giữ nguyên: miễn phí sử dụng và nhúng, không phải
open source. Đọc LICENSE.txt trước khi dùng.

## Giới hạn đã biết

- Optical chưa có hint căn nét lên lưới (chỉ smart dropout); các font tĩnh có hint vẫn được cung cấp.
- Chưa kiểm Windows/ClearType và Safari/WebKit. Kiểm trình duyệt trước phát hành dùng Chromium 155 trên macOS.
- FontBakery universal còn năm FAIL ở bộ Optical: ba `opentype/fvar/regular_coords_correct`, một `opentype/fsselection` và một `opentype/mac_style`. Đây là các check giả định family có instance Regular/trục wght, trong khi mỗi font giữ weight cố định và chỉ có opsz. Kiểm riêng name, weight class và style bits trong `verify_optical.py`; không tắt check và không tuyên bố FontBakery xanh.
- Chưa có italic, ExtraBold, SemiBold riêng, trục wght, số proportional, phân số, mũi tên, Hy Lạp hay Cyrillic. Số mặc định tabular.

Bản 1.0 kế thừa hình và spacing của ứng viên 0.301; tăng version và cập nhật tài liệu phát hành.
Kết quả kiểm bản 1.000 và checksum được đính kèm trong GitHub Release.

## Kiểm tra bản 1.000

- `scripts/verify.py`: 213 pass, 0 fail, 12 info.
- `scripts/verify_optical.py`: 156 pass, 0 fail (gồm OTS, name/metrics, trục opsz, shape/advance và GPOS).
- FontBakery 1.1.0 universal chạy riêng: TTF 314 pass / 0 fail; OTF 278 pass / 0 fail; Optical TTF 366 pass / 5 fail như mô tả trên.
- So với 0.301: đủ 20 font chỉ thay metadata phiên bản trong head/name/CFF; các bảng khác giữ nguyên.
- Build và đóng gói hai lần: 21/21 SHA-256 khớp (20 font + ZIP). ZIP có đúng 22 mục, CRC và nội dung khớp nguồn.
