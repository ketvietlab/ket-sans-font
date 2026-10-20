# KÉT Sans — Font Design System

Phiên bản 0.300 · Phase 1 (Foundation) + Phase 2 (Core glyphs) + Phase 4a (GF Latin Core +
tiếng Việt + ₫) + Phase 4b (Light, Regular, Medium, Bold).

Nguồn sự thật duy nhất là [`design-system.json`](design-system.json). Mọi glyph được sinh từ các
thông số đó bằng `scripts/ketsans/`. Các bảng ở mục 9 được sinh tự động từ JSON và từ số đo trên
font đã build. `scripts/verify.py` sẽ fail nếu tài liệu lệch khỏi hệ thống. Muốn đổi một thông
số thì sửa JSON, chạy `scripts/build.py`, rồi kiểm lại bằng `scripts/verify.py`.

## 1. DNA

KÉT Sans là một neo-grotesque trung tính dành cho giao diện phần mềm tiếng Việt. Mục tiêu là
cảm giác **Clean · Neutral · Precise · Professional**: đặt cạnh SF Pro hay Inter thì cùng nhóm
chất lượng, nhưng có nhịp và tỷ lệ riêng. Sau góp ý trên hai bản thử trước ("quá cá tính",
"cách điệu quá mạnh", "nhìn SF Pro là biết"), bản này cố ý giữ phần nhận diện ở mức gần như
không nhận ra ngay.

**Học gì từ ba font tham chiếu.** Các con số dưới đây chỉ là đo đạc toàn cục (UPM 2048, Regular).
KÉT Sans không đọc, trace hay chỉnh outline, kerning hay dữ liệu nào của các font này.

| | SF Pro (opsz 17) | Inter (opsz 14) | Be Vietnam Pro | KÉT Sans |
| --- | --- | --- | --- | --- |
| Cap / x-height (em) | 0.705 / 0.526 | 0.728 / 0.546 | 0.740 / 0.530 | 0.711 / 0.531 |
| Stem n / H (đơn vị) | 174 / 180 | 180 / 190 | 195 / 201 | 182 / 192 |
| Tương phản O (đỉnh/cạnh) | 0.90 | 0.95 | 0.91 | 0.87 |

- **Từ Inter:** x-height lớn để đọc tốt ở 11–13 px, tương phản thấp, hệ stem rõ ràng.
- **Từ SF Pro:** độ chính xác quang học, đường cong căng nhưng không hình học cứng, nhịp đều,
  chỗ vai nối vào stem có khía rõ.
- **Từ Be Vietnam Pro:** dấu tiếng Việt đủ lớn, đủ đậm, đặt cân với thân chữ; cách xếp dấu
  chồng theo quy ước Việt.

**Trên thang trung tính, KÉT Sans đứng giữa SF Pro và Inter.** Độ đậm Regular nhỉnh hơn SF một
chút để chữ trông "vững chãi" (stem 182 so với 174), và x-height nằm giữa hai font.

## 2. Đặc điểm nhận diện (bốn điểm, áp dụng nhất quán)

1. **Đầu nét cắt theo lưới.** Mọi terminal được cắt đúng phương ngang (c e s a 2, C G J S, 3 5 6
   9, ?) hoặc đúng phương dọc (r t f 1). Không có đầu nét xiên hay bo tròn. Đây là nét
   neo-grotesque cổ điển, cho cảm giác điềm tĩnh và chắc.
2. **Tròn đầy.** Bụng chữ dùng độ căng 0.59 bên ngoài và 0.58 bên trong; đường tròn thật là
   0.552. Counter đi theo mặt ngoài nên nét giữ 0.94 độ dày cạnh ở góc chéo, không thắt kiểu
   ngòi bút (bản trước 0.57/0.60 thắt còn 0.89). Khe mở khép như SF (c 0.39 x-height) và s có
   gáy thoải, nên chữ đọc thành khối tròn chứ không thành nét bút.
3. **Vai có đo lường.** Vai và bụng rời stem ở trên cao và dốc (0.88 x-height, 76°). Counter
   của n chạm stem ở 0.65 x-height, đúng chỗ SF, Inter, Be Vietnam Pro đặt (0.65–0.67), nên
   counter tròn và khía rõ ở 11–13 px mà không có nêm xiên kiểu nét bút. Bản đầu dùng 0.835 / 62° /
   0.60 và bị chê "lai viết tay"; bản kế đẩy nách lên 0.72 thì counter vuông, vai cứng.
4. **Dấu Việt chung một ngòi bút.** Mọi dấu dùng chung nét `markStroke` và chung độ căng với
   chữ. Sau dấu mũ, dấu sắc/huyền/hỏi đặt lệch phải với khoảng hở được giải ra cụ thể; dấu ngã
   và mọi dấu sau dấu trăng chồng dọc. Râu ơ ư là một gờ ngang uốn lên thành thân đứng, dày gần
   bằng nét chữ.

Không glyph nào mang chi tiết trang trí riêng. Nhận diện đến từ tỷ lệ, nhịp và lối hoàn thiện.

## 3. Stroke system

- **Phân cấp stem:** chữ hoa 192, chữ thường 182. Hai stem của n bằng nhau (182); stem của m
  là 174 (ba stem cần nhẹ hơn để mật độ đều). Stem đứng của N là 176 còn nét chéo của N là 190, theo
  cách neo-grotesque dồn trọng lượng vào nét chéo.
- **Nét ngang:** ngang chữ hoa 170 (0.89 so với stem hoa), ngang chữ thường 154. Ở E, tay giữa
  mỏng hơn 6 và tay dưới dày hơn 6 so với tay trên để cân thị giác.
- **Cạnh tròn:** cạnh tròn dày hơn stem cùng loại khoảng 3% (O 198, o 188) để bù cảm giác mảnh
  của đường cong. Đỉnh/đáy tròn mỏng hơn (O 172, o 162).
- **Đường chéo:** dày theo phương vuông góc với nét (A, V 184). Bề ngang của nét chéo được giải
  ra từ góc nghiêng, nên độ đậm cảm nhận khớp với stem đứng.
- **Nét phụ của số:** mảnh hơn thân số như SF, Inter, Helvetica (0.76–0.94): sống 2 ×0.84,
  chéo 4 ×0.78, nét đứng 5 ×0.88 và nghiêng 0.11 (đỉnh lệch phải).
- **Giao điểm:** vai và bụng rời stem gần phương đứng rồi mới uốn, nên chỗ nối mỏng đi nhờ một
  nách ngắn, không dùng ink trap và không có nêm xiên. Đỉnh A và đáy V là mặt phẳng hẹp (204), không nhọn,
  để không tụ mực.
- **Chuyển tiếp thẳng–cong:** tiếp tuyến liên tục G1 ở mọi điểm trên đường. Đoạn cong dùng độ
  căng đo theo giao điểm tiếp tuyến, nên mọi bụng, vai và đầu nét nói chung một ngôn ngữ cong.

## 4. Shape system

| Khía cạnh | Quy tắc |
| --- | --- |
| Aperture | c cắt ở 0.36/0.39 bán kính tính từ tâm, khe 0.39 x-height bằng SF; C và G ở 0.39/0.42; e cắt dưới ở 0.42. Móc a là vai chữ n (uốn từ 0.66 x-height) phủ một oval rộng gần hết chữ; phần tư trái cắt ngang ở 0.25 bán kính trên tâm, tức 0.75 x-height. s (và S $ §) là hai oval chồng nhau: điểm cực ở 0.725/0.285 chiều cao, đầu nét cắt ở 0.12/0.10 bán kính tính từ điểm cực, oval trên thụt 0.035 bề rộng mỗi bên. |
| Gáy s | Hai mép gáy rời điểm cực đứng của hai oval và qua tâm với góc 12°, cách nhau 0.92 cạnh s, độ căng 0.65. Đo trên raster gáy nghiêng 14°, như SF, Inter và Helvetica; bản trước 21° nên đọc thành một dải xéo. |
| Counter | Counter dùng độ căng 0.58, theo sát mặt ngoài (0.59). Counter của số 0 dùng 0.60 để giữ độ mở trong khung hẹp. |
| Oval | O, o, 0 là superellipse bốn điểm cực trị; khung trong lệch đúng độ dày cạnh/đỉnh. |
| Vai (n h m r u) | Rời stem ở 0.88 x-height với tiếp tuyến 76°; đỉnh ngoài ở 0.55 bề rộng; cạnh phải dựng đứng từ 0.66 x-height. Nách ở 0.65 x-height, vào stem ở 254°. |
| Bụng (b d p q) | Một nửa vòng nối stem như vai, đối xứng quanh x/2: nối ở 0.88/0.12 x-height với góc 76°, nách ở 0.72/0.28 với góc 74°. d là gốc; b = d lật ngang; q = bụng d + stem descender; p = q lật ngang. Bụng a có đỉnh thẳng dốc 3° tới 0.55 bề rộng bụng rồi vào một phần tư oval; đáy nối stem ở 0.15 x-height với góc 76°, viền trong rời stem theo phương đứng ở 0.36 x-height. |
| Terminal | Cắt ngang (c e s a 2) hoặc dọc (r t 1). Không cắt xiên. |
| Join | Mọi chỗ nối giữ khía ngoài rõ ràng (n tại 0.88 x); nách n ở 0.65 x, nách bụng d ở 0.72 x. Đỉnh bụng a gặp stem ở 0.615 x. |
| Stem alignment | Đỉnh stem phẳng đúng x-height, cap height hoặc ascender. Overshoot chỉ áp cho phần tròn. |
| Curve tension | Xem bảng C ở mục 9. Đổi một giá trị tension sẽ đổi đồng loạt mọi glyph dùng nó. |

## 5. Proportion system

- Bề rộng thân: n : o : H : O = 0.77 : 0.88 : 1 : 1.16. Chữ thường hơi rộng (nhịp UI thoáng);
  O rộng hơn H vì một vòng tròn trông hẹp hơn hai stem.
- Chữ hoa so với chữ thường: x/cap = 0.747, bằng tỷ lệ của SF Pro (0.747) và gần Inter (0.750).
- Số là **tabular** (1280 đơn vị) theo mặc định để cột số trong bảng ERP thẳng hàng. Thân 0 rộng
  1000.
- Nhịp và độ đậm thị giác: kiểm bằng chuỗi `HOHOH`, `nonon`, `nmnhnunr` ở mục 8 của specimen.

## 6. Spacing system và kerning

- Sidebearing theo hình dạng cạnh (bảng F). Cạnh thẳng chữ hoa 184. Cạnh tròn chữ hoa 116, tức
  0.63 cạnh thẳng. Cạnh chéo chữ hoa 18. Chữ thường: cạnh thẳng trái 160, cạnh thẳng phải
  n/h/m 148 (đẩy nhịp về phía trước), cạnh tròn 106, đầu nét của c là 70.
- Kerning chỉ sửa những cặp mà sidebearing không xử lý được (chéo–chéo, chéo–tròn, tay mở T F L
  P, ngoặc kép và dấu chấm). Mỗi nhóm kerning mang tên chữ đại diện cho một hình dạng cạnh
  (`public.kern1.O` gồm O D Q G B Þ Ø Đ; `public.kern2.V` gồm V W). Mọi chữ dựng sẵn tự vào
  nhóm của chữ gốc, nên `ẤV` kern giống `AV`. Các chữ có râu (ơ ư Ơ Ư) và các chữ có caron dạng
  phẩy (ď ľ ť Ľ) chỉ vào nhóm phía cạnh không đổi, vì dấu đã đổi cạnh phải.
- **Ngoại lệ chống va chạm:** sau khi áp giá trị nhóm, `kerning.py` dựng profile trái/phải của
  từng glyph (cả dấu) ở mỗi 16 đơn vị chiều cao. Cặp nào cách nhau dưới 60 đơn vị sẽ có ngoại lệ
  riêng, nới giá trị vừa đủ để giữ 60. Ví dụ T + í chỉ nới từ −110 về −92, còn T + ï và V + ĩ
  nhận giá trị dương vì dấu chạm cánh chữ hoa ngay cả khi không kern.
- Không kern các cặp thẳng/tròn với nhau (HH, nn, oo) và không kern số tabular. `verify.py`
  kiểm cả hai điều này, và đo lại khoảng cách ≥ 50 cho mọi cặp có kern.

## 7. Bản đồ kế thừa glyph

| Master | Glyph kế thừa |
| --- | --- |
| stem + bar | H I E N l i ı 1, gạch nối; F (E bỏ tay dưới), L, T, Ħ ħ Ł ł (thêm gạch), Æ (chân trái A + E) |
| ring | O o 0, chấm (i, chấm câu, dấu nặng); Q (vòng + đuôi thẳng), Ø ø, 8 (hai vòng chung eo ở 0.52 cap, vòng trên rộng 0.89), 6 (viền theo oval của 0, bụng nối vào nét như vai n, đầu nét cắt ngang gần sát mép phải), 9 (6 xoay 180°), ° |
| arch (n) | h (stem ascender), m (hai vai, counter ×0.92), r (vai cắt dọc), u (n xoay 180°); ß (stem vươn thành vòm); 5 (nét đứng nghiêng, bụng rời nét như vai n, đầu nét dưới ngang 3) |
| bowl (d) | b, p, q (lật/ghép stem); g (bụng q + đuôi móc của a), þ (bụng p + stem suốt), đ (thêm gạch) |
| side bowl | D (đường cong của O, tay phẳng), Đ Ð (thêm gạch), P, R (bụng P + chân thẳng từ eo), B (hai bụng, bụng trên hẹp 72), Þ, Œ, phần dưới của ẞ |
| cut ring | c (vòng o cắt ngang), e (vòng o + thanh ngang + cắt dưới); C, G (góc dưới phải dựng đứng ở GJoin, thanh dày như H) |
| cup | U (stem H ×0.98 vào đường cong O); J (stem H vào chén U, cắt như c) |
| hook stem | t (stem + thanh x-height, móc ngắn uốn từ 0.20 x-height, cắt dọc; hai mép đuôi cùng nhích nửa overshoot nên đuôi chạy phẳng, không hất lên); f (móc t lật lên ascender); ȷ j; £ |
| diagonal | A (đỉnh phẳng, thanh thấp), V (A lật, bỏ thanh), N (stem ×0.92 + chéo đậm); M W X Y Z K, v w x y z k (ở x-height, nét `diagonalLower`), 4 (thanh ở 0.215 cap, vươn 0.14 cap qua thân), 7 |
| spine | s (hai oval cắt như c + gáy thoải), a (móc là vai n phủ oval rộng, cắt như c + bụng đỉnh thẳng, đáy nối dài vào stem), 2 (đỉnh như a + sống lưng một đường cong + chân dày như thanh hoa); S (s ở cap height), $, § (s và chính nó xoay 180° quanh bụng dưới, khép thành một vòng), 3 (đỉnh như 2 + hai bụng, eo ở 0.52 cap), ? (đỉnh như 2 thành stem giữa); & (nửa trên một oval: cạnh trái chạy thẳng xuống thành chân 48°, cạnh phải bẻ xuống trái thành bụng, bụng vươn lên thành đuôi cắt ngang) |

Mỗi glyph trong UFO lưu ghi chú kế thừa ở `lib["vn.ketviet.construction"]`; specimen hiển thị
ghi chú này ở mục phóng to glyph. Một thay đổi ở master lan sang mọi glyph trong cùng hàng.
`verify.py` đo lại stem, nét ngang, overshoot và sidebearing sau mỗi lần build.

## 8. Hệ thống tiếng Việt

- **Thiết kế từ đầu:** line box (1960/−520) đã chừa chỗ cho hai tầng dấu. Dấu chữ thường nằm
  cách x-height 152 (khoảng hở đo được 0.117 x-height, như SF và Inter). Dấu `.case` cho chữ hoa
  dẹt hơn và nằm cách cap height 96. Chồng cao nhất là Ỗ, chạm đúng 2048 (1 em, giới hạn verify).
  Phần vượt typo ascender được win metrics phủ, nên không bị cắt.
- **Chữ hoa tròn:** anchor `top` của O C G Q S nằm cao hơn cap height nửa overshoot, để dấu
  trên chữ tròn nhìn cách thân bằng dấu trên chữ thẳng.
- **Dấu:** sắc/huyền gần đều nét (đầu 162, chân 144; vuốt mạnh sẽ thành nét cọ), cắt ngang và căn tâm theo khung.
  Dấu hỏi là bụng mở trên một đuôi đứng (dấu "?" không chấm), cùng một contour. Dấu ngã là một
  sóng có đầu cắt dọc. Dấu mũ có đỉnh phẳng như chữ A, rộng 650. Dấu trăng là nửa vòng, đầu cắt
  ngang, rộng 630. Dấu nặng dùng chấm của chữ i (1.32 stem, như 3 font tham chiếu 1.29–1.41).
  Râu mọc từ một điểm trên mép ngoài của chữ ở 0.90 x-height (0.93 cap height với Ơ Ư): mép dưới
  rời vai gần nằm ngang (6°) rồi dựng đứng, mép trong thẳng đứng, góc trong bo nhỏ, đỉnh cắt ngang
  ở 1.24 x-height (1.17 cap height). Nét râu 162 (168 với `.case`).
- **Xếp chồng:** trong `circumflexcomb_{acute,grave,hookabove}comb`, dấu thứ hai được trượt
  sang trái cho tới khi cách dấu mũ đúng 44 đơn vị (36 với `.case`); chân dấu thứ hai đặt ở 92 %
  chiều cao dấu mũ (60 % với `.case`). Dấu ngã và mọi dấu sau dấu trăng chồng dọc, cách nhau 58
  (36 với `.case`).
- **Chữ dựng sẵn:** là composite đặt theo anchor `top`, `bottom`, `horn`. Các chữ ơ ư Ơ Ư và
  đ Đ có outline riêng (râu/gạch được hợp vào chữ khi build). Ð dùng chung outline với Đ.
- **Dấu Latin:** cùng ngòi bút với dấu Việt. ď ľ ť Ľ dùng `caroncomb.alt` (caron dạng phẩy) đặt ở
  anchor `topright`, và chữ được nới bề rộng tới mép phải của dấu. Ģ Ķ Ļ Ņ ķ ļ ņ dùng phẩy dưới thay
  cho cedilla, ģ dùng phẩy ngược bên trên. Cedilla và ogonek gắn vào anchor `bottom`/`ogonek` và
  được hợp vào outline, nên chỗ nối không có overlap.
- **Chuỗi dấu kết hợp:** `ccmp` thay i/j → ı/ȷ khi có dấu trên, đổi dấu sang `.case` sau chữ
  hoa, ghép cặp dấu Việt, ghép o/u/O/U + râu thành ơ/ư/Ơ/Ư, đổi caron sang dạng phẩy sau d l t L
  và cedilla sang phẩy dưới sau G K L N k l n. `mark`/`mkmk` được sinh từ anchor. `verify.py`
  render từng chữ dựng sẵn (NFC) và so pixel với chuỗi NFD được định vị bằng GPOS trên một bản
  font đã bỏ cmap của chữ dựng sẵn. Kết quả phải trùng từng pixel, trừ ≤ 4 px ở chỗ nối của
  cedilla/ogonek (bản dựng sẵn hợp outline, bản GPOS thì chồng hai glyph).
- **Phạm vi Phase 4a:** đủ 134 chữ tiếng Việt và toàn bộ GF Latin Core (419 codepoint trong
  [`charset.txt`](charset.txt), 241 chữ dựng sẵn).

## 9. Thông số (sinh tự động)

<!-- GENERATED:START (scripts/document.py) -->

### A. Vertical metrics

| Thông số | Giá trị | Tỷ lệ | Quan hệ |
| --- | --- | --- | --- |
| UPM | 2048 | 1.000 em | lưới TrueType chuẩn, đủ mịn cho overshoot và dấu |
| Baseline | 0 | 0 | mọi chân nét phẳng đứng đúng 0 |
| x-height | 1088 | 0.531 em | x/cap = 0.747 |
| Cap height | 1456 | 0.711 em | chữ hoa, số lining |
| Ascender (b d h l) | 1520 | 0.742 em | cao hơn cap 64 để tách l khỏi I |
| Descender (p q) | -420 | 0.205 em |  |
| Overshoot tròn hoa / số | 28 | 1.9% cap | O, 0 |
| Overshoot tròn thường | 22 | 2.0% x | o c e s a b d p q |
| Overshoot vai | 18 | 1.7% x | đỉnh vai n h m r, đáy u |
| Typo ascender / descender / gap | 1960 / -520 / 0 | 1.211 em | line box mặc định; win metrics lấy từ bounds thật |


### B. Stroke system (Light, Regular, Medium, Bold)

| Tham số | Light | Light ÷ Regular | Regular | ÷ stemLower | Medium | Bold | ÷ stemLower | Bold ÷ Regular |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stemUpper | 146 | ×0.76 | 192 | 1.055 | 232 | 312 | 1.061 | ×1.62 |
| stemLower | 142 | ×0.78 | 182 | 1.000 | 219 | 294 | 1.000 | ×1.62 |
| stemLowerRight | 142 | ×0.78 | 182 | 1.000 | 219 | 294 | 1.000 | ×1.62 |
| stemM | 136 | ×0.78 | 174 | 0.956 | 207 | 272 | 0.925 | ×1.56 |
| barUpper | 131 | ×0.77 | 170 | 0.934 | 198 | 254 | 0.864 | ×1.49 |
| barLower | 119 | ×0.77 | 154 | 0.846 | 173 | 210 | 0.714 | ×1.36 |
| barE | 122 | ×0.79 | 154 | 0.846 | 167 | 194 | 0.660 | ×1.26 |
| roundUpperSide | 152 | ×0.77 | 198 | 1.088 | 241 | 326 | 1.109 | ×1.65 |
| roundUpperTop | 134 | ×0.78 | 172 | 0.945 | 198 | 250 | 0.850 | ×1.45 |
| roundLowerSide | 145 | ×0.77 | 188 | 1.033 | 229 | 310 | 1.054 | ×1.65 |
| roundLowerTop | 126 | ×0.78 | 162 | 0.890 | 186 | 234 | 0.796 | ×1.44 |
| archTop | 126 | ×0.79 | 160 | 0.879 | 184 | 232 | 0.789 | ×1.45 |
| diagonalUpper | 149 | ×0.81 | 184 | 1.011 | 221 | 294 | 1.000 | ×1.60 |
| diagonalN | 154 | ×0.81 | 190 | 1.044 | 228 | 304 | 1.034 | ×1.60 |
| stemN | 137 | ×0.78 | 176 | 0.967 | 213 | 286 | 0.973 | ×1.62 |
| figureSide | 149 | ×0.77 | 194 | 1.066 | 236 | 320 | 1.088 | ×1.65 |
| figureTop | 129 | ×0.78 | 166 | 0.912 | 191 | 240 | 0.816 | ×1.45 |
| figureStem | 146 | ×0.77 | 190 | 1.044 | 229 | 308 | 1.048 | ×1.62 |
| sSide | 140 | ×0.77 | 182 | 1.000 | 221 | 300 | 1.020 | ×1.65 |
| markStroke | 123 | ×0.78 | 158 | 0.868 | 177 | 214 | 0.728 | ×1.35 |
| diagonalLower | 139 | ×0.81 | 172 | 0.945 | 207 | 276 | 0.939 | ×1.60 |
| diagonalM | 139 | ×0.81 | 172 | 0.945 | 207 | 276 | 0.939 | ×1.60 |
| bowlWaist | 120 | ×0.77 | 156 | 0.857 | 179 | 226 | 0.769 | ×1.45 |
| punctStroke | 117 | ×0.78 | 150 | 0.824 | 175 | 224 | 0.762 | ×1.49 |
| hairStroke | 100 | ×0.78 | 128 | 0.703 | 145 | 180 | 0.612 | ×1.41 |


Light — tương phản ngang/dọc: H 0.90, O 0.88, o 0.87, vai n 0.89. Bù quang học cạnh tròn: O +4.1% so với stem hoa, o +2.1% so với stem thường.


Regular — tương phản ngang/dọc: H 0.89, O 0.87, o 0.86, vai n 0.88. Bù quang học cạnh tròn: O +3.1% so với stem hoa, o +3.3% so với stem thường.


Medium — tương phản ngang/dọc: H 0.85, O 0.82, o 0.81, vai n 0.84. Bù quang học cạnh tròn: O +3.9% so với stem hoa, o +4.6% so với stem thường.


Bold — tương phản ngang/dọc: H 0.81, O 0.77, o 0.75, vai n 0.79. Bù quang học cạnh tròn: O +4.5% so với stem hoa, o +5.4% so với stem thường.


Light: Light from the Regular -> Light change measured on SF Pro (opsz 17) and Inter (opsz 14) at 300/400 (rasters, x-height normalised; Helvetica Light sits near 200 and is left out). Unlike Bold, Light is not on the Regular -> Bold line: SF and Inter thin horizontals as much as verticals (contrast kept) and keep advances (x0.98-1.00), so the counters open. Strokes: stems x0.78 (cap stem x0.76, figure stem x0.77), round sides x0.77, round tops x0.78, arch x0.79, bars x0.77, e bar x0.79, diagonals x0.81; marks and punctuation thin with the stem (x0.78). Widths: Regular + g x (Light - Regular stem), g = SF/Inter mean per shape (n 0.55, m 0.65, o 0.5, c 0.7, e 0.4, a 0.8, d 0.65, s 0.75, r 0.85, t 1.0, f 1.0, v 0.8, w 0.4, x 0.55, y 0.85, z 0.6, k 1.3, H 0.8, N 0.55, M 0.75, U 0.65, J 0.6, K 1.2, E F 0.6, L 0.5, T 0.45, Z 0.6, B 0.75, P 0.9, R 0.95, D 0.55, O 0.5, G 0.55, C 0.4, S 0.7, A V 0.7, W 0.8, X 0.85, Y 0.7, figure 0.5); tabular advance x0.995. Sidebearings x1.06. Dots shrink less than stems (dot/stem x1.12), mark dots x1.05, mark width x0.94. Apertures as measured: c opens x1.11 (terminals x1.11), e x1.18 (lower terminal 0.485), figures and ? barely (terminalClose -0.005); C a s S keep their Regular cuts (G shares C's cut and stays, where SF/Inter open it x1.08).


Bold: Derived from Regular by the Regular→Bold change measured on SF Pro, Inter and Helvetica rasters (x-height units): stems ×1.62, round sides ×1.65, round tops and shoulders ×1.45, capital bars ×1.49, lowercase bars ×1.36, diagonals ×1.6, marks ×1.35. Body width = Regular + g × added stem weight, g per letter shape from the mean of SF and Inter (n 1.0, o 0.6, d 0.75, H 0.75, O 0.45 …). Sidebearings ×0.85.


Medium: Weights between the masters are interpolated from the masters' own parameters, not drawn: every stroke, shape, proportion, spacing and curve value is Regular + t (Bold - Regular) with t = (wght - 400) / (700 - 400), and the same recipes run on the result. SF and Inter put 500 at t 0.29-0.38 on every measured stroke, aperture and advance (rasters, x-height normalised), i.e. linear in wght, so Medium uses t = 1/3. Medium also serves CSS weight 600 (UI semibold): declare its face as font-weight 500 600, otherwise browsers pick Bold for 600. Strokes, widths and spacing round to whole units, shapes to 4 decimals.


### C. Curve tension

| Tham số | Giá trị | Ghi chú |
| --- | --- | --- |
| outer | 0.59 |  |
| inner | 0.58 |  |
| shoulderOuter | 0.6 |  |
| shoulderInner | 0.58 |  |
| terminal | 0.62 |  |
| circle | 0.5523 |  |


Tension measured against the tangent intersection; 0.5523 is a true circle. Outer curves are a touch firmer than circular and counters follow them a hair rounder, so the stroke keeps its weight round the bowl instead of thinning at the diagonals.


### D. Shape ratios

| Tham số | Light | Regular | Medium | Bold |
| --- | --- | --- | --- | --- |
| barUpperCenter | = | 0.51 | = | = |
| barLowerE | = | 0.462 | = | = |
| archJoinOuter | = | 0.88 | = | = |
| archCrotch | = | 0.65 | 0.64 | 0.62 |
| archJoinAngle | = | 76 | = | = |
| archCrotchAngle | = | 254 | = | = |
| archApexX | = | 0.55 | = | = |
| archRightTangent | = | 0.66 | = | = |
| bowlJoinOuter | = | 0.88 | = | = |
| bowlCrotch | = | 0.72 | 0.71 | 0.69 |
| bowlJoinAngle | = | 76 | = | = |
| bowlCrotchAngle | = | 74 | = | = |
| cTerminalUpper | 0.4 | 0.36 | 0.3293 | 0.268 |
| cTerminalLower | 0.433 | 0.39 | 0.3567 | 0.29 |
| eTerminalLower | 0.485 | 0.42 | 0.3943 | 0.343 |
| aBarUpper | = | 0.275 | = | = |
| aTerminal | = | 0.25 | 0.23 | 0.19 |
| aHookLeft | = | 0.04 | = | = |
| aBowlTop | = | 0.615 | = | = |
| aBowlSlope | = | 3 | = | = |
| aBowlCorner | = | 0.55 | = | = |
| aBowlJoin | = | 0.15 | = | = |
| aBowlCrotch | = | 0.36 | = | = |
| dotDiameter | 1.478 | 1.32 | 1.2367 | 1.07 |
| dotGap | = | 0.2 | = | = |
| markWidth | 0.94 | 1.0 | 1.05 | 1.15 |
| markDot | 1.113 | 1.06 | 0.9933 | 0.86 |
| markDotCase | 1.05 | 1.0 | 0.9367 | 0.81 |
| terminalClose | -0.005 | 0.0 | 0.0073 | 0.022 |
| sExtremeUpper | = | 0.725 | = | = |
| sExtremeLower | = | 0.285 | = | = |
| sSpineAngle | = | 12 | = | = |
| sSpineWeight | = | 0.92 | = | = |
| sSpineTension | = | 0.65 | = | = |
| sUpperInset | = | 0.035 | = | = |
| sTerminalUpper | = | 0.12 | 0.0933 | 0.04 |
| sTerminalLower | = | 0.1 | 0.07 | 0.01 |
| tTop | = | 0.892 | = | = |
| tHookBend | = | 0.2 | = | = |
| BWaist | = | 0.535 | = | = |
| PBowlBottom | = | 0.4 | = | = |
| CTerminalUpper | = | 0.39 | 0.3653 | 0.316 |
| CTerminalLower | = | 0.42 | 0.3933 | 0.34 |
| GBarTop | = | 0.52 | = | = |
| GJoin | = | 0.3 | = | = |
| UJoin | = | 0.31 | = | = |
| KArmRoot | = | 0.3 | = | = |
| YJoin | = | 0.44 | = | = |
| mathAxis | = | 0.45 | = | = |
| jTerminal | = | 0.62 | = | = |
| hornRoot | = | 0.9 | = | = |
| HornRoot | = | 0.93 | = | = |


Ratios: bar heights are fractions of cap/x-height, join heights fractions of x-height, terminal cuts fractions of the bowl radius from its centre. a: aHookLeft is a fraction of the letter width, aBowlCorner of the bowl width, aBowlSlope is in degrees.


### E. Proportions (bề rộng thân)

| Glyph/nhóm | Light | Regular | ÷ H | ÷ n | Medium | Bold | Bold − Regular |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H | 1099 | 1136 | 1.000 | 1.297 | 1166 | 1226 | +90 |
| O | 1297 | 1320 | 1.162 | 1.507 | 1338 | 1374 | +54 |
| E | 902 | 930 | 0.819 | 1.062 | 952 | 996 | +66 |
| A | 1284 | 1316 | 1.158 | 1.502 | 1352 | 1424 | +108 |
| V | 1264 | 1296 | 1.141 | 1.479 | 1328 | 1392 | +96 |
| N | 1119 | 1144 | 1.007 | 1.306 | 1172 | 1228 | +84 |
| n | 854 | 876 | 0.771 | 1.000 | 913 | 988 | +112 |
| m | 1448 | 1474 | 1.298 | 1.683 | 1517 | 1603 | +129 |
| o | 984 | 1004 | 0.884 | 1.146 | 1026 | 1071 | +67 |
| d | 974 | 1000 | 0.880 | 1.142 | 1028 | 1084 | +84 |
| c | 947 | 975 | 0.858 | 1.113 | 997 | 1042 | +67 |
| e | 974 | 990 | 0.871 | 1.130 | 1012 | 1057 | +67 |
| s | 834 | 864 | 0.761 | 0.986 | 899 | 970 | +106 |
| a | 848 | 880 | 0.775 | 1.005 | 908 | 964 | +84 |
| r | 538 | 572 | 0.504 | 0.653 | 607 | 678 | +106 |
| t | 600 | 640 | 0.563 | 0.731 | 668 | 724 | +84 |
| figure | 977 | 1000 | 0.880 | 1.142 | 1041 | 1124 | +124 |
| tabularAdvance | 1274 | 1280 | 1.127 | 1.461 | 1307 | 1360 | +80 |
| B | 966 | 1000 | 0.880 | 1.142 | 1030 | 1090 | +90 |
| C | 1222 | 1240 | 1.092 | 1.416 | 1262 | 1306 | +66 |
| D | 1185 | 1210 | 1.065 | 1.381 | 1230 | 1270 | +60 |
| F | 852 | 880 | 0.775 | 1.005 | 902 | 946 | +66 |
| G | 1245 | 1270 | 1.118 | 1.450 | 1288 | 1324 | +54 |
| J | 832 | 860 | 0.757 | 0.982 | 900 | 980 | +120 |
| K | 1075 | 1130 | 0.995 | 1.290 | 1170 | 1250 | +120 |
| L | 827 | 850 | 0.748 | 0.970 | 872 | 916 | +66 |
| M | 1366 | 1400 | 1.232 | 1.598 | 1434 | 1502 | +102 |
| P | 969 | 1010 | 0.889 | 1.153 | 1040 | 1100 | +90 |
| R | 1016 | 1060 | 0.933 | 1.210 | 1090 | 1150 | +90 |
| S | 1048 | 1080 | 0.951 | 1.233 | 1108 | 1164 | +84 |
| T | 1079 | 1100 | 0.968 | 1.256 | 1122 | 1166 | +66 |
| U | 1090 | 1120 | 0.986 | 1.279 | 1138 | 1174 | +54 |
| W | 1783 | 1820 | 1.602 | 2.078 | 1850 | 1910 | +90 |
| X | 1171 | 1210 | 1.065 | 1.381 | 1246 | 1318 | +108 |
| Y | 1178 | 1210 | 1.065 | 1.381 | 1244 | 1312 | +102 |
| Z | 1012 | 1040 | 0.915 | 1.187 | 1062 | 1106 | +66 |
| f | 570 | 610 | 0.537 | 0.696 | 634 | 683 | +73 |
| k | 848 | 900 | 0.792 | 1.027 | 937 | 1012 | +112 |
| v | 953 | 985 | 0.867 | 1.124 | 1020 | 1091 | +106 |
| w | 1454 | 1470 | 1.294 | 1.678 | 1515 | 1604 | +134 |
| x | 928 | 950 | 0.836 | 1.084 | 987 | 1062 | +112 |
| y | 956 | 990 | 0.871 | 1.130 | 1027 | 1102 | +112 |
| z | 816 | 840 | 0.739 | 0.959 | 861 | 902 | +62 |


### F. Spacing (sidebearing theo hình dạng cạnh)

| Nhóm cạnh | Light | Regular | ÷ thẳng cùng loại | Medium | Bold | ÷ thẳng cùng loại |
| --- | --- | --- | --- | --- | --- | --- |
| upperStraight | 195 | 184 | 1.00 | 175 | 156 | 1.00 |
| upperRound | 123 | 116 | 0.63 | 110 | 99 | 0.63 |
| upperDiagonal | 19 | 18 | 0.10 | 17 | 15 | 0.10 |
| lowerStraight (trái) | 170 | 160 | 1.00 | 152 | 136 | 1.00 |
| lowerStraightRight (phải n h m) | 157 | 148 | 0.93 | 141 | 126 | 0.93 |
| lowerRound | 112 | 106 | 0.66 | 101 | 90 | 0.66 |
| lowerTerminal (c) | 74 | 70 | 0.44 | 67 | 60 | 0.44 |


### G. Đo trên font đã build (OTF)


Light

| Glyph | Advance | LSB | RSB | yMin | yMax |
| --- | --- | --- | --- | --- | --- |
| H | 1489 | 195 | 195 | 0 | 1456 |
| O | 1543 | 123 | 123 | -28 | 1484 |
| I | 536 | 195 | 195 | 0 | 1456 |
| E | 1225 | 195 | 112 | 0 | 1456 |
| A | 1322 | 19 | 19 | 0 | 1456 |
| V | 1302 | 19 | 19 | 0 | 1456 |
| N | 1501 | 191 | 191 | 0 | 1456 |
| n | 1181 | 170 | 157 | 0 | 1106 |
| o | 1208 | 112 | 112 | -22 | 1110 |
| h | 1181 | 170 | 157 | 0 | 1520 |
| p | 1256 | 170 | 112 | -420 | 1110 |
| d | 1256 | 112 | 170 | -22 | 1520 |
| b | 1256 | 170 | 112 | -22 | 1520 |
| q | 1256 | 112 | 170 | -420 | 1110 |
| a | 1097 | 92 | 157 | -22 | 1110 |
| e | 1188 | 112 | 102 | -22 | 1110 |
| c | 1103 | 112 | 74 | -22 | 1110 |
| s | 1018 | 93 | 92 | -22 | 1110 |
| r | 744 | 170 | 36 | 0 | 1106 |
| t | 636 | 20 | 40 | -22 | 1356 |
| u | 1181 | 157 | 170 | -18 | 1088 |
| m | 1775 | 170 | 157 | 0 | 1106 |
| i | 482 | 136 | 136 | 0 | 1515 |
| l | 482 | 170 | 170 | 0 | 1520 |
| 0 | 1274 | 148 | 148 | -28 | 1484 |
| 1 | 1274 | 300 | 488 | 0 | 1456 |
| 2 | 1274 | 148 | 138 | 0 | 1484 |


Regular

| Glyph | Advance | LSB | RSB | yMin | yMax |
| --- | --- | --- | --- | --- | --- |
| H | 1504 | 184 | 184 | 0 | 1456 |
| O | 1552 | 116 | 116 | -28 | 1484 |
| I | 560 | 184 | 184 | 0 | 1456 |
| E | 1242 | 184 | 112 | 0 | 1456 |
| A | 1352 | 18 | 18 | 0 | 1456 |
| V | 1332 | 18 | 18 | 0 | 1456 |
| N | 1504 | 180 | 180 | 0 | 1456 |
| n | 1184 | 160 | 148 | 0 | 1106 |
| o | 1216 | 106 | 106 | -22 | 1110 |
| h | 1184 | 160 | 148 | 0 | 1520 |
| p | 1266 | 160 | 106 | -420 | 1110 |
| d | 1266 | 106 | 160 | -22 | 1520 |
| b | 1266 | 160 | 106 | -22 | 1520 |
| q | 1266 | 106 | 160 | -420 | 1110 |
| a | 1120 | 92 | 148 | -22 | 1110 |
| e | 1192 | 106 | 96 | -22 | 1110 |
| c | 1127 | 106 | 70 | -22 | 1110 |
| s | 1048 | 93 | 92 | -22 | 1110 |
| r | 768 | 160 | 36 | 0 | 1106 |
| t | 676 | 20 | 40 | -22 | 1356 |
| u | 1184 | 148 | 160 | -18 | 1088 |
| m | 1782 | 160 | 148 | 0 | 1106 |
| i | 502 | 131 | 131 | 0 | 1546 |
| l | 502 | 160 | 160 | 0 | 1520 |
| 0 | 1280 | 140 | 140 | -28 | 1484 |
| 1 | 1280 | 282 | 468 | 0 | 1456 |
| 2 | 1280 | 140 | 130 | 0 | 1484 |


Medium

| Glyph | Advance | LSB | RSB | yMin | yMax |
| --- | --- | --- | --- | --- | --- |
| H | 1516 | 175 | 175 | 0 | 1456 |
| O | 1558 | 110 | 110 | -28 | 1484 |
| I | 582 | 175 | 175 | 0 | 1456 |
| E | 1255 | 175 | 112 | 0 | 1456 |
| A | 1386 | 17 | 17 | 0 | 1456 |
| V | 1362 | 17 | 17 | 0 | 1456 |
| N | 1514 | 171 | 171 | 0 | 1456 |
| n | 1206 | 152 | 141 | 0 | 1106 |
| o | 1228 | 101 | 101 | -22 | 1110 |
| h | 1206 | 152 | 141 | 0 | 1520 |
| p | 1281 | 152 | 101 | -420 | 1110 |
| d | 1281 | 101 | 152 | -22 | 1520 |
| b | 1281 | 152 | 101 | -22 | 1520 |
| q | 1281 | 101 | 152 | -420 | 1110 |
| a | 1141 | 92 | 141 | -22 | 1110 |
| e | 1204 | 101 | 91 | -22 | 1110 |
| c | 1145 | 101 | 67 | -22 | 1110 |
| s | 1083 | 93 | 92 | -22 | 1110 |
| r | 795 | 152 | 36 | 0 | 1106 |
| t | 704 | 20 | 40 | -22 | 1356 |
| u | 1206 | 141 | 152 | -18 | 1088 |
| m | 1810 | 152 | 141 | 0 | 1106 |
| i | 523 | 126 | 126 | 0 | 1576 |
| l | 523 | 152 | 152 | 0 | 1520 |
| 0 | 1307 | 133 | 133 | -28 | 1484 |
| 1 | 1307 | 277 | 461 | 0 | 1456 |
| 2 | 1307 | 133 | 123 | 0 | 1484 |


Bold

| Glyph | Advance | LSB | RSB | yMin | yMax |
| --- | --- | --- | --- | --- | --- |
| H | 1538 | 156 | 156 | 0 | 1456 |
| O | 1572 | 99 | 99 | -28 | 1484 |
| I | 624 | 156 | 156 | 0 | 1456 |
| E | 1280 | 156 | 112 | 0 | 1456 |
| A | 1454 | 15 | 15 | 0 | 1456 |
| V | 1422 | 15 | 15 | 0 | 1456 |
| N | 1532 | 152 | 152 | 0 | 1456 |
| n | 1250 | 136 | 126 | 0 | 1106 |
| o | 1251 | 90 | 90 | -22 | 1110 |
| h | 1250 | 136 | 126 | 0 | 1520 |
| p | 1310 | 136 | 90 | -420 | 1110 |
| d | 1310 | 90 | 136 | -22 | 1520 |
| b | 1310 | 136 | 90 | -22 | 1520 |
| q | 1310 | 90 | 136 | -420 | 1110 |
| a | 1182 | 92 | 126 | -22 | 1110 |
| e | 1227 | 90 | 80 | -22 | 1110 |
| c | 1178 | 90 | 60 | -22 | 1110 |
| s | 1154 | 92 | 92 | -22 | 1110 |
| r | 850 | 136 | 36 | 0 | 1106 |
| t | 760 | 20 | 40 | -22 | 1356 |
| u | 1250 | 126 | 136 | -18 | 1088 |
| m | 1865 | 136 | 126 | 0 | 1106 |
| i | 566 | 126 | 126 | 0 | 1620 |
| l | 566 | 136 | 136 | 0 | 1520 |
| 0 | 1360 | 118 | 118 | -28 | 1484 |
| 1 | 1360 | 268 | 444 | 0 | 1456 |
| 2 | 1360 | 118 | 108 | 0 | 1484 |



### H. Đặc điểm nhận diện

| Đặc điểm | Quy tắc |
| --- | --- |
| Grid-cut terminals | Every terminal is cut exactly horizontal (c, e, s, a, 2) or exactly vertical (r, t, 1). No diagonal or rounded ends. |
| Full round | Bowls use tension 0.59 outside and 0.58 inside (circle = 0.552): the counter follows the outline, so the stroke keeps 0.94 of its side weight at the diagonals; apertures close like SF (c 0.39 x-height) and s has a shallow spine, so letters read as round forms, not pen strokes. |
| Measured shoulder | Shoulders and bowls leave the stem high and steep (0.88 x-height, 76°); the n counter meets the stem at 0.65 x-height, where SF, Inter and Be Vietnam Pro put it (0.65–0.67), so the counter stays round and the notch reads at 11–13 px without a pen-like wedge. |
| Vietnamese marks drawn in the same pen | Marks share one stroke (markStroke 158) and the full-round curve and sit 152 units over the x-height; after a circumflex the acute, grave and hook rise from 92 % of its height on its upper right with a solved 44-unit clearance; the horn is a level shelf turning into an upright stub cut horizontally at 1.24 x-height. |

<!-- GENERATED:END -->

## 10. Weights (Phase 4b)

Family có bốn độ đậm. Light (300), Regular (400) và Bold (700) là master dựng từ JSON. Medium (500)
là instance nội suy và cũng dùng cho chữ 600 của giao diện. ExtraBold, SemiBold riêng và variable
font chưa dựng.

**Master.** Mỗi master có `stroke` riêng trong `masters.<tên>` và có thể ghi đè `shapes`,
`proportions`, `spacing`, `curves`; `System._layer` gộp giá trị chung với phần ghi đè. Mọi master
chạy cùng một bộ recipe. Hằng số hình học trong recipe (đỉnh phẳng của A V, đuôi phẩy, nét ký
hiệu, cỡ dấu…) được nhân với hệ số bằng đúng 1 ở Regular:
- `wk = stemLower ÷ stemLower(Regular)` cho nét;
- `mk = markStroke ÷ markStroke(Regular)` cho nét dấu;
- `gk = 1 + 0.7 (mk − 1)` cho hình dấu.

Vì vậy thêm weight không đổi glyph nào của Regular. Điều này đã được kiểm bằng cách so từng file
glyph trong source Regular trước và sau.

**Bold lấy từ đâu.** Tỷ lệ Bold ÷ Regular được đo trên raster SF Pro (opsz 17), Inter (opsz 14)
và Helvetica, chuẩn theo x-height, rồi áp lên chính Regular của KÉT:
- **Nét:** thân ×1.62, cạnh tròn ×1.65, đỉnh tròn và vai ×1.45, ngang hoa ×1.49, ngang thường
  ×1.36, ngang e ×1.26, chéo ×1.6, thân M ×1.56, nét dấu ×1.35, dấu câu ×1.5, nét mảnh ×1.4.
- **Bề rộng:** Regular + g × (stem Bold − stem Regular). g là trung bình của SF và Inter theo
  hình chữ: n 1.0, m 1.15, o c e 0.6, H 0.75, O 0.45, số 1.05…; giá trị đầy đủ nằm ở bảng E.
- **Khoảng trắng:** sidebearing ×0.85.
- **Khe mở:** khép lại một chút (`terminalClose` 0.022, cùng đầu nét riêng của c C e a s), vẫn
  nằm trong khoảng của SF và Inter.

**Light lấy từ đâu.** Light không nằm trên đường Regular → Bold, nên không ngoại suy được. Đo
raster SF Pro và Inter ở 300/400:
- nét ngang mảnh đi bằng đúng tỷ lệ nét đứng (tương phản giữ nguyên), trong khi lên Bold nét
  ngang tăng chậm hơn;
- advance gần như giữ nguyên (×0.98–1.00).

Ngoại suy t = −1/3 vì thế sẽ cho nét ngang dày quá và chữ hẹp đi khoảng 4%. Helvetica Light nhẹ
cỡ 200 (t ≈ −0.6) nên không dùng. Light là master riêng, lấy tỷ lệ Light ÷ Regular trung bình của
SF và Inter:
- **Nét:** thân ×0.78 (thân hoa ×0.76, thân số ×0.77), cạnh tròn ×0.77, đỉnh tròn ×0.78, vai
  ×0.79, ngang ×0.77, ngang e ×0.79, chéo ×0.81; dấu và dấu câu mảnh theo thân (×0.78).
- **Bề rộng:** Regular + g × (stem Light − stem Regular), với g đo riêng cho Light (n 0.55,
  o 0.5, H 0.8, O 0.5, số 0.5…; đủ trong comment của master và bảng E). Advance tabular ×0.995.
- **Khoảng trắng:** sidebearing ×1.06.
- **Chấm:** nhỏ đi ít hơn thân (chấm ÷ thân ×1.12, chấm của dấu ×1.05); bề rộng dấu ×0.94.
- **Khe mở theo số đo:** c ×1.11, e ×1.18, số và ? gần như giữ (`terminalClose` −0.005). C, a, s,
  S giữ đường cắt của Regular. G dùng chung đường cắt với C nên cũng giữ, trong khi SF/Inter mở G
  ×1.08.

Sau khi build, KÉT Light nằm giữa SF và Inter 300 ở mọi số đo: thân n 0.133 x-height (SF 0.130,
Inter 0.122), counter n ×1.11, advance ×0.99–1.00.

Recipe chỉ cần sửa một chỗ cho Light: vòng % vốn lớn lên khi nét dày, giờ không co lại khi nét
mảnh, để lòng vòng mở ra như SF.

**Medium là instance, không vẽ riêng.** Mục `instances` trong JSON chỉ khai báo độ đậm.
`system.py` nội suy mọi giá trị số của stroke, shapes, proportions, spacing và curves theo công
thức Regular + t (Bold − Regular), với t = (wght − 400) ÷ 300. Nét, bề rộng và spacing làm tròn về
đơn vị nguyên, shapes làm tròn 4 chữ số, rồi chạy cùng recipe.

Lý do Medium dùng t = 1/3: đo raster SF và Inter ở 400/500/600/700, mọi nét, khe mở và advance
của 500 nằm ở t 0.29–0.38 (và của 600 ở 0.64–0.71), tức tuyến tính theo wght. Sau khi build, KÉT
500 cách SF và Inter 500 trong 1–5%; thân n là 0.200 so với 0.195/0.198 x-height.

**Chữ 600 dùng Medium.** Ngày 20-10, instance 600 (t = 2/3) bị chê vẫn quá đậm cho giao diện.
Theo yêu cầu, nó được thay bằng 500, và chữ 600 dùng Medium. Việc này nằm ở khai báo CSS, không
nằm trong file font: face Medium khai báo `font-weight: 500 600`. Nếu không, luật chọn weight của
CSS lấy Bold cho 600. Specimen, preview và README dùng đúng khai báo này.

**Đặt tên.** Regular và Bold là một style-map family (bit Regular/Bold, macStyle). Medium là
Regular của family riêng `KET Sans Medium` (name ID 1/2), và nhóm vào `KET Sans` bằng
typographic name (ID 16/17), theo cách Google Fonts đặt tên static ngoài RIBBI. Vertical metrics
và underline giống nhau ở mọi weight.

**Giới hạn đã biết.**
- Dấu trên chữ hoa của Medium và Bold dẹt hơn SF, vì chồng dấu phải nằm trong 1 em.
- Source giữ các contour dựng hình chồng lên nhau, nhưng vài glyph được gộp outline ngay trong
  recipe khi cần: `untangled` cho offset tự gập, `united` cho § khi phép gộp một lần thất bại. Vì
  thế tương thích điểm giữa các master chưa được kiểm, và chưa có variable font.

## 11. Font engineering

`design-system.json` → `scripts/ketsans` → UFO3 (`sources/`) → fontmake (TTF và OTF chạy riêng,
overlap gỡ bằng pathops, composite lồng được làm phẳng) → ttfautohint (TTF) → WOFF2. Timestamp
được cố định nên hai lần build cho ra checksum giống hệt. Chi tiết ở [README](README.md).
