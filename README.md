# KÉT Sans

Typeface thương hiệu của Két Việt: neo-grotesque trung tính cho giao diện tiếng Việt.

**Trạng thái: Phase 4b.** Đủ bảng chữ GF Latin Core + tiếng Việt + ₫ ở bốn độ đậm: Light (300),
Regular (400), Medium (500) và Bold (700). Bold và Light được dựng theo yêu cầu ngày 20-10. Medium là instance nội suy và
cũng dùng cho chữ 600 của giao diện ([Dùng trên web](#dùng-trên-web)). Diễn biến ngày 20-10:
- góp ý "font 600 quá đậm": khi đó trình duyệt lấy Bold cho chữ 600;
- tui thêm một SemiBold nội suy;
- góp ý tiếp: thay bản 600 đó bằng 500 và cho chữ 600 dùng 500.

Cả bộ đang chờ duyệt. ExtraBold và SemiBold riêng chưa dựng.

- Hệ thống thiết kế: [FONT-DESIGN-SYSTEM.md](FONT-DESIGN-SYSTEM.md)
- Thông số (nguồn sự thật duy nhất): [design-system.json](design-system.json)
- Bảng chữ mục tiêu: [charset.txt](charset.txt) (419 codepoint, sinh một lần từ glyphsets 1.1.3)
- Specimen: [specimen/index.html](specimen/index.html)
- Giấy phép: [LICENSE.txt](LICENSE.txt). Freeware độc quyền như SF Pro, không phải open source: ai cũng
  được tải và dùng miễn phí, kể cả cho thương mại và nhúng vào web, app hay PDF, nhưng không được sửa
  hoặc phân phối lại file font. Gói tải về chỉ chứa font, license và README; source ở repo này không phát hành.

## Có gì trong Phase 4b

| | |
| --- | --- |
| Độ đậm | Light 300, Regular 400 và Bold 700 là master; Medium 500 là instance nội suy ở 1/3 quãng Regular → Bold, dùng cho cả 500 và 600 ([mục 10](FONT-DESIGN-SYSTEM.md#10-weights-phase-4b)) |
| Bảng chữ | 419 codepoint, 449 glyph: A–Z, a–z, Æ Œ Ø Ð Þ Ł Ħ ẞ, ı ȷ ß æ œ ø ð þ ħ ł ª º, số 0–9, dấu câu, tiền tệ `$ ¢ £ ¥ € ₫`, toán `+ − × ÷ = < > ~ ^`, `° © ® ™ § ¶ @ & #` |
| Dấu | 18 dấu kết hợp, 12 dấu `.case`, `caroncomb.alt` (caron dạng phẩy cho ď ľ ť Ľ), 8 cặp dấu chồng tiếng Việt (mỗi cặp có `.case`), 13 dấu đứng riêng (´ ¨ ˆ ˜ …) |
| Chữ dựng sẵn | 241 chữ có dạng tách NFD: 132 chữ Việt có dấu và các chữ Latin Core (Ą Č Ğ Ő Ș Ţ Ź …). Composite đặt theo anchor; cedilla và ogonek được hợp vào outline. đ Đ Ł Ø… vẽ riêng |
| OpenType | `ccmp` (i/j → ı/ȷ, dấu `.case`, cặp dấu Việt, ghép râu, caron dạng phẩy, cedilla thành phẩy dưới ở Ģ Ķ Ļ Ņ ķ ļ ņ và phẩy ngược trên ģ), `mark`/`mkmk` sinh từ anchor, `kern` theo nhóm hình dạng |
| Kerning | 81 cặp nhóm + 109 ngoại lệ chống va chạm do máy tính từ outline |
| Định dạng | `fonts/ttf` (hint bằng ttfautohint), `fonts/otf` (CFF), `fonts/woff2` (~20 KB mỗi weight) |
| Source | `sources/KETSans-{Light,Regular,Medium,Bold}.ufo` (UFO3, sinh từ hệ thống, mở được bằng mọi trình sửa font) |

Chưa có: ExtraBold, SemiBold riêng, variable font, số proportional (`pnum`), phân số, số mũ, mũi tên, Latin
mở rộng ngoài Core, Hy Lạp/Cyrillic. Specimen tô màu mọi ký tự ngoài bảng chữ để không nhầm với
KÉT Sans.

## Build

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/build.py     # JSON → UFO → TTF/OTF/WOFF2 → specimen data → bảng tài liệu
.venv/bin/python scripts/verify.py    # kiểm thử cấu trúc, kiểu chữ, tiếng Việt, tài liệu
.venv/bin/python scripts/package.py   # gói tải về: build/dist/KETSans-<version>.zip
```

Gói zip chứa `LICENSE.txt`, `README.txt` (từ `package/README.txt`) và các thư mục `OTF/`, `TTF/`, `WOFF2/`.
Gói cũng tái lập được: các mục được sắp thứ tự và đóng dấu cùng `SOURCE_DATE_EPOCH` với bản build.

Build tái lập được: cùng source thì cho cùng checksum, vì `SOURCE_DATE_EPOCH` được cố định và
không có bước nào ghi lại timestamp. Vòng thiết kế nhanh: `scripts/draft.py [glyph…]` biên dịch
ngay trong process và ghi proof PNG vào `build/draft/` (không commit); đặt
`KETSANS_MASTER=Light`, `Medium` hoặc `Bold` để dựng weight khác.

Xem specimen bằng một HTTP server tĩnh chạy ở gốc repo:

```sh
python3 -m http.server 8765        # tại gốc repo
open http://127.0.0.1:8765/specimen/index.html
```

Muốn so với Inter, chép `InterVariable.woff2` (OFL, tải từ rsms.me/inter) vào `specimen/ref/`. Thư
mục này không được commit; nếu thiếu, specimen dùng Inter cài trong máy nếu có. SF Pro và Be
Vietnam Pro được lấy từ font cài trong máy.

## Dùng trên web

Medium gánh cả weight 500 và 600. Face của nó phải khai báo dải `500 600`. Nếu không, trình duyệt
lấy Bold cho chữ 600, vì theo luật chọn weight của CSS, với 600 nó tìm face nặng hơn trước.

```css
@font-face { font-family: "KÉT Sans"; src: url(KETSans-Light.woff2) format("woff2"); font-weight: 300; }
@font-face { font-family: "KÉT Sans"; src: url(KETSans-Regular.woff2) format("woff2"); font-weight: 400; }
@font-face { font-family: "KÉT Sans"; src: url(KETSans-Medium.woff2) format("woff2"); font-weight: 500 600; }
@font-face { font-family: "KÉT Sans"; src: url(KETSans-Bold.woff2) format("woff2"); font-weight: 700; }
```

Chữ đặt 800–900 dùng Bold cho tới khi có ExtraBold; 100–200 dùng Light.

## Cấu trúc

```text
design-system.json        metrics, stroke, tension, shape, proportion, spacing, identity
charset.txt               bảng chữ mục tiêu (verify.py kiểm độ phủ theo file này)
LICENSE.txt               giấy phép sử dụng (tiếng Việt là bản chính, kèm bản tiếng Anh)
package/README.txt        README của gói tải về
scripts/ketsans/
  geometry.py             đường cong theo tiếp tuyến + độ căng, cắt contour, biến đổi, offset
  glyphs.py               master construction (stem, ring, arch, bowl, cut ring, diagonal, spine,
                          side bowl, cup, hook stem, S) và bộ glyph nền tảng
  upper.py, lower.py      chữ hoa và chữ thường còn lại, dựng từ các master trên
  figures.py, punct.py    số 3–9; dấu câu, tiền tệ, toán, ký hiệu
  latin.py                gộp các recipe thành một builder
  marks.py                dấu, cặp dấu, chữ dựng sẵn từ charset.txt, ccmp
  kerning.py              nhóm kerning theo hình dạng cạnh, ngoại lệ chống va chạm
  ufo.py, master.py       ghi UFO3
  cleanup.py              bộ lọc fontmake: bỏ điểm không mang hình sau khi gộp overlap
  measure.py, proof.py    ray-casting đo nét; proof PNG bằng FreeType + HarfBuzz
scripts/build.py          build chính thức
scripts/verify.py         bộ kiểm thử
scripts/document.py       sinh bảng thông số trong FONT-DESIGN-SYSTEM.md
scripts/specimen_data.py  xuất outline thật từ OTF cho specimen
scripts/package.py        đóng gói zip để phát hành
sources/  fonts/  specimen/
```

Giá trị cấp hệ thống (metrics, stroke, tension, tỷ lệ, spacing) nằm trong JSON. Tỷ lệ chỉ riêng
một glyph dùng (vị trí điểm cực trị của s, góc sống lưng của 2, eo của 3…) nằm ngay trong recipe
của glyph đó.

## Kiểm thử

`scripts/verify.py` chạy trên UFO và ba file đã build của từng weight, rồi kiểm cả family:

- **Cấu trúc:** độ phủ đủ 419 codepoint của `charset.txt`; unicode không trùng; contour kín,
  không suy biến, tọa độ nguyên; không contour tự cắt; composite trỏ đúng và phẳng; outline đã
  build không còn overlap; đủ bảng OpenType; OpenType Sanitizer (bộ kiểm của trình duyệt) cho
  TTF/OTF/WOFF2; win metrics phủ mọi bounds; fsType cài đặt được.
- **Kiểu chữ:** 120 kỳ vọng cao độ/overshoot; 44 phép đo stem và 17 phép đo nét ngang/tròn so
  với hệ stroke (±3); sidebearing theo nhóm cạnh (thẳng, tròn, bụng, chén, mở, chéo); kerning có
  tác dụng (kể cả chữ có dấu qua nhóm của chữ gốc); không kern cặp thẳng/tròn và số; 24 glyph số,
  tiền tệ, toán cùng một bề rộng tabular; mọi cặp có kern (11.760 cặp glyph) vẫn cách nhau ít nhất
  50 đơn vị, tính cả dấu.
- **Dấu và chữ dựng sẵn:** 241 chữ dựng sẵn (NFC) và 20 từ trùng từng pixel với chuỗi NFD định
  vị bằng GPOS (cho phép ≤ 4 px ở chỗ nối của cedilla/ogonek, vì chỗ đó được hợp outline);
  `ccmp` cho 13 trường hợp; dấu cách thân chữ ít nhất 70 đơn vị (caron dạng phẩy ≥ 40); dấu chồng
  cách nhau ít nhất 34 đơn vị (kiểm bằng giao diện tích); dấu đơn căn tâm ±6.
- **Tiếng Việt:** chồng cao nhất không vượt 1 em; 10 chuỗi bắt buộc của brief có đủ glyph.
- **Family:** cùng glyph order và cmap; vertical metrics giống nhau; style linking (usWeightClass,
  fsSelection, macStyle, name ID 1/2/16/17); mỗi weight đậm hơn weight trước (n H o O).
- **Tài liệu:** bảng trong FONT-DESIGN-SYSTEM.md khớp với JSON và với font đã build.

Mutation test ở Phase 2 (chạy trên bản sao ở `/tmp`, không commit) xác nhận bộ kiểm thử bắt được:
stem sai 12 đơn vị, dấu chồng chạm nhau, mất ngữ cảnh `.case`, composite lệch 20 đơn vị, mất cặp
kerning AV. Các kiểm thử mới của Phase 4a đã fail trên lỗi thật trước khi sửa: T + ĩ và ř chạm
nhau khi kern (dẫn tới ngoại lệ chống va chạm); dấu trên chữ hoa tròn, vòng `.case` và phẩy dưới
cách thân dưới 70 đơn vị; outline của chữ có cedilla/ogonek còn overlap trong TTF. Kiểm thử
NFC/NFD còn từng bắt được một lỗi build: chạy `fontmake -o ttf otf`
trong cùng một lần gọi làm phần rã composite của CFF lây sang TTF. Vì vậy `build.py` gọi fontmake
riêng cho từng định dạng.

Bản Bold đầu tiên của Phase 4b bị verify bắt nhiều lỗi thật:
- ß và ª tự cắt;
- ť và ỵ chạm dấu;
- Šťastný ở dạng NFC lệch NFD;
- chồng dấu cao quá 1 em;
- dấu `.case` cách thân dưới 70.

FontBakery bắt thêm ba lỗi:
- hai nét ˝ dính nhau;
- ẞ thừa contour;
- độ dày underline lệch giữa các weight.

Khi thêm weight nội suy đầu tiên (600), phép gộp outline lúc build hỏng ở §: vòng tròn và bụng s trùng khít một đường
cong. Recipe giờ gộp sẵn khi phép gộp một lần thất bại (`united`), nên Regular và Bold không đổi.

FontBakery (`check-universal`) cho 0 FAIL, 0 WARN khi chạy riêng từng file TTF/OTF của cả bốn
weight, và cả khi chạy cả family (TTF, OTF).

## Cần đánh giá

Ba câu hỏi Phase 3 chưa được chốt. Phase 4a/4b tạm theo mặc định hiện có để vẽ tiếp:

1. **Đầu nét cắt ngang/dọc** (đặc điểm nhận diện số 1). Kiểm lại ngày 20-10 trên ảnh phóng to:
   SF Pro (Text và Display) và Helvetica cũng cắt c, s nằm ngang, chỉ Inter cắt xiên gần vuông
   góc với nét. Đề xuất giữ lối cắt theo lưới vì nó khớp với SF; vẫn chờ chốt.
2. **Cỡ hiển thị:** trong Chromium, KÉT rộng ngang SF ở 13–14 px. Từ 16 px trở lên, KÉT rộng hơn
   3–8% vì SF tự siết tracking theo optical size. Có hai cách: thêm trục `opsz`, hoặc đặt token
   letter-spacing âm cho cỡ ≥ 20 px. Chưa có `opsz`.
3. **Số mặc định tabular:** thẳng cột trong bảng, nhưng thưa trong câu chữ (`HN-0012`). Tiền tệ
   và dấu toán giờ cũng tabular để thẳng cột với số. `pnum` chưa có.

Những hình cần mắt người duyệt ở Phase 4a:

4. Các chữ hoa có nhiều lựa chọn kiểu: G không có cựa, R chân thẳng mọc từ eo, Q đuôi thẳng cắt
   ngang, K chân mọc từ tay, M đỉnh giữa phẳng chạm baseline, ẞ.
5. g một tầng (bụng q + đuôi móc của a), y đuôi thẳng, ß, @, số 3–9 (đặc biệt eo của 3 và 8).
   6 và 9 đã vẽ lại theo oval của số 0 sau góp ý "quá cá tính".
6. Dấu trên chữ hoa tròn (O C G Q S) cao hơn dấu trên chữ hoa thẳng nửa overshoot (14 đơn vị),
   để khoảng hở nhìn bằng nhau. Vì vậy dấu Việt trên Ô Ơ cũng cao hơn bản Phase 2.
7. Ỗ cao tới 2048 (đúng 1 em), vượt typo ascender 1960 nhưng vẫn nằm trong win metrics
   (winAscent 2048). Ở line-height 1.0 có thể chạm dòng trên.
8. Tinh chỉnh còn treo từ Phase 2: cờ số 1 hơi ngắn và mảnh; độ sâu nách trong A ở cỡ nhỏ.
9. Sửa theo góp ý 20-10 ("cứng, không thẳng, lai viết tay"), cần duyệt lại bằng mắt:
   - vai và bụng (n m h r u b d p q a g) rời stem cao và dốc, nách ngắn kiểu neo-grotesque thay cho
     nêm xiên;
   - móc t/f ngắn;
   - dấu sắc/huyền gần đều nét;
   - râu ư/ơ thành cung ngắn chìa ra phải (đã thay ở mục 11).

   Độ lệch tâm khối mực giữa nửa trên và nửa dưới của n m h u t về ngang SF/Helvetica (đo trong
   lúc làm, không có trong verify). s, a và móc t của lần này đã được thay ở mục 10.

10. Sửa theo góp ý 20-10 lần hai ("chưa đạt, phải tròn, vẫn viết tay, mặt chữ không phẳng").
    Đo trên raster cạnh SF, Inter, Helvetica (chỉ đo, không đọc outline) cho thấy ba nguyên nhân:
    viền trong vuông hơn viền ngoài nên nét o thắt ở góc chéo (0.89 độ dày cạnh, SF 0.95); c mở
    quá rộng (khe 0.53 x-height, SF 0.39); gáy s dốc 21° và nặng (SF 14°). Đã sửa:
    - độ căng 0.59 ngoài / 0.58 trong: nét ở góc chéo 0.944, o vẫn tròn hơn SF (độ vuông 2.13 so
      với 2.25);
    - khe c 0.39 x-height, C 0.42 cap height, e 0.18;
    - s S $ dựng lại từ hai oval cắt như c và một gáy thoải 14°, dày 0.92 stem; § là s và chính
      nó xoay 180° khép thành vòng; & vẽ lại theo bố cục neo-grotesque (vòng, chân 48°, bụng, đuôi);
    - móc a là đỉnh oval cắt như c, bụng a rời stem nằm ngang (a đã dựng lại ở mục 12); đuôi
      t/f/j chạy phẳng, không hất;
    - hai stem của n bằng nhau (182); ngoặc nhọn có tay cong thay cho tay phẳng.

    Các số đo này không nằm trong verify. Cần duyệt bằng mắt ở cỡ đọc và cỡ lớn.

11. Sửa theo góp ý 20-10 lần ba ("chữ a nhỏ, dấu móc còn méo"). Đo theo từng họ chữ cạnh SF,
    Inter, Be Vietnam Pro (chỉ rasterize, cùng x-height, độ dày chia cho stem của chính font đó):
    - râu ơ ư: nét 0.46 stem và đỉnh 0.995 x-height, trong khi 3 font kia là 0.75–0.86 và
      1.21–1.28. Đã vẽ lại thành gờ ngang uốn lên thân đứng, đỉnh 1.24 x-height;
    - a: bụng thấp và bè (counter 0.23 so với 0.26–0.27; bụng rộng 0.55 so với 0.50–0.51).
      Đỉnh bụng nâng lên 0.615 x-height, a hẹp lại 2%;
    - dấu sát chữ (khoảng hở 0.09 so với 0.12), dấu mũ/trăng hẹp, dấu nặng nhỏ (1.05 so với
      1.36 stem), ố chồng thấp (0.47 so với 0.68–0.73). Đã nâng, nới rộng và phóng các dấu này;
    - nách n 0.74 x-height so với 0.65–0.67, làm counter vuông. Đã đặt về 0.65;
    - c, v, w, x, y hẹp hơn 4–5%, đuôi t dài, đỉnh t thấp. Đã chỉnh về khoảng của 3 font.

    Sau khi sửa, 3 chỉ số còn lệch, mỗi chỉ số ≤ 5%: nét dấu trăng, nét râu ơ, diện tích râu Ơ. Các số
    đo này không nằm trong verify.

12. Sửa theo góp ý 20-10 lần bốn ("chữ a phá vỡ độ trung tính, biến font thành font cá tính").
    So ở 300 px cạnh SF, Inter, Helvetica, a của mục 10–11 có hai chỗ lạ:
    - móc là một vòm hẹp và nhọn: oval chỉ phủ từ 0.10 bề rộng, hai bên bắt đầu uốn ngay từ đỉnh
      bụng (0.6 x-height), đầu nét thụt vào trong;
    - bụng là một thấu kính dẹt: đỉnh cong đều từ stem sang trái, đáy chạy ngang tới tận stem rồi
      mới gập vào.

    Đã dựng lại a từ chính các master của KÉT:
    - móc là vai chữ n (uốn từ 0.66 x-height như n) phủ một oval rộng gần hết chữ; đầu nét cắt
      ngang như c, ở 0.75 x-height (SF 0.75, Inter 0.73);
    - bụng có đỉnh thẳng dốc 3° rời stem ở 0.615 x-height, góc trên trái là một phần tư oval
      (độ căng 0.59/0.58); đáy nối stem ở 0.15 x-height, viền trong rời stem theo phương đứng ở
      0.36 x-height nên counter tròn, không có góc nhọn.

    Số đo theo họ chữ sau khi sửa: rộng mực / n 1.006 (SF 0.994, Inter 1.013), dày đỉnh móc 0.87
    stem (0.88/0.89), rộng bụng 0.51 x-height (0.50/0.51), counter bụng 0.25 (0.27/0.26), đáy đầu
    móc 0.75 (0.75/0.73). æ và ª dựng từ a nên đổi theo. Các số đo này không nằm trong verify.

13. So bộ số 0–9 theo yêu cầu 20-10. Đo trên raster cạnh SF, Inter, Helvetica: chuẩn theo cap height,
    độ dày chia cho stem H của chính font đó. Có 9 chỉ số nằm ngoài khoảng của ba font, phần lớn do
    nét phụ của số đậm bằng thân:
    - sống 2 dày 1.00 stem (0.83–0.87), chéo 4 0.95 (0.76–0.85), nét đứng 5 1.00 và dựng thẳng
      (0.78–0.94, nghiêng 5–8° với đỉnh lệch phải);
    - eo 3 cao 0.554 cap (0.50–0.52); thanh 4 cao 0.313 (0.26–0.29) và chỉ vươn 0.118 qua thân
      (0.135–0.144); đầu nét dưới của 5 thấp 0.219 (0.25–0.26);
    - bụng 9 cao 0.376 (0.33–0.35) vì bụng 6 thấp; 8 có counter trên gần cao bằng counter dưới (0.96,
      ba font 0.80–0.92).

    Đã sửa: sống 2 ×0.84; chéo 4 ×0.78, thanh 4 hạ xuống 0.215 cap và vươn 0.14 cap; nét đứng 5
    ×0.88, nghiêng 0.11, đầu nét dưới ở 0.25 cap như 3; eo 3 ở 0.52; đỉnh bụng 6 lên 0.645 (9 theo);
    eo 8 lên 0.52, vòng trên rộng 0.89. Sau khi sửa, mọi chỉ số của bộ số đều nằm trong khoảng của
    ba font. Advance tabular 0.879 cap gần SF và Inter khi bật `tnum` (0.894 và 0.891); mặc định
    của hai font đó là số proportional (câu hỏi 3). Các số đo này không nằm trong verify.

14. Bold (yêu cầu 20-10) và Medium (góp ý "font 600 quá đậm", rồi "thay 600 bằng 500"):
    - Bold: tỷ lệ nét Bold ÷ Regular khớp SF; khe mở của c e a s C G 2 3 5 6 S nằm trong khoảng
      SF/Inter.
    - Medium cách SF và Inter 500 trong 1–5% (thân n 0.200 so với 0.195/0.198 x-height). So với chữ
      600 của SF thì nhẹ hơn rõ (thân n 0.233).

    Cần mắt người duyệt:
    - chữ 500 và 600 trên preview CRM và web giờ đều là Medium;
    - dấu trên chữ hoa của Medium và Bold dẹt hơn SF, vì chồng dấu phải nằm trong 1 em;
    - R trong ® nhỏ so với vòng (mọi weight);
    - chữ đặt 800 (tiêu đề trang chủ ketviet-web) hiển thị bằng Bold vì chưa có ExtraBold.
15. Light (yêu cầu 20-10). Không nằm trên đường Regular → Bold:
    - SF và Inter làm mảnh nét ngang bằng đúng tỷ lệ nét đứng, nên tương phản giữ nguyên (lên Bold
      thì nét ngang tăng chậm hơn);
    - advance gần như giữ nguyên (×0.98–1.00), nên counter rộng ra khoảng 10%.

    Vì vậy Light là master riêng, lấy tỷ lệ Light ÷ Regular đo trên SF và Inter. Helvetica Light
    nhẹ cỡ 200 nên không dùng. Sau khi build, KÉT Light nằm giữa SF và Inter 300 ở mọi số đo:
    - thân n 0.133 x-height (SF 0.130, Inter 0.122);
    - counter n ×1.11, advance ×0.99–1.00, sidebearing ×1.05;
    - khe c ×1.11, khe e ×1.18;
    - đầu nét của số đổi ≤ 2%, như SF/Inter.

    Cần mắt người duyệt:
    - G không mở thêm (SF/Inter mở ×1.08), vì G dùng chung đường cắt với C, mà C phải giữ nguyên;
    - vòng % hẹp và cao hơn SF ở mọi weight (đặc điểm có sẵn từ Regular). Ở Light, cỡ vòng giữ
      bằng Regular thay vì co theo nét như trước khi sửa.

16. Tự review trước khi phát hành (20-10). FontBakery bản googlefonts và soát toàn bộ charset ở Light
    và Bold bắt được, rồi đã sửa:
    - į, ị chưa mất chấm khi có dấu trên;
    - chân W, w, y có bậc 2–8 đơn vị;
    - chấm của . : ; ! ? … lệch 2 đơn vị;
    - điểm thừa ở Œ, ¶;
    - « ‹ bị lấp khe ở Medium và Bold, lề lệch ở mọi weight.

    Còn chờ mắt người: « ‹ cao 0.48 x-height, trong khi SF 0.78, Inter 0.84 (đặc điểm có sẵn từ
    Phase 3).

Chưa kiểm: hiển thị trên Windows/ClearType (không có máy Windows) và Safari/WebKit (trình duyệt
kiểm thử chỉ có Chromium).

## Nguyên tắc

Không dùng ảnh do AI tạo; không sao chép, trace hay chỉnh outline, kerning hay dữ liệu của SF Pro,
Inter hay Be Vietnam Pro. Font tham chiếu chỉ được rasterize để so sánh và đo số liệu toàn cục.
Mọi outline của KÉT Sans được sinh từ `design-system.json` bằng mã trong repo này.
