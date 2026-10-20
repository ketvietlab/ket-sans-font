KÉT Sans {version}

Phông chữ thương hiệu của Két Việt: neo-grotesque trung tính cho giao diện tiếng Việt.
Miễn phí tải và sử dụng, kể cả cho mục đích thương mại và nhúng vào website, ứng dụng, tài
liệu. Không được sửa hay phân phối lại các tệp phông. Điều khoản đầy đủ ở LICENSE.txt.

Đây là bản beta: glyph, khoảng cách và kerning còn có thể đổi ở bản sau.

Trong gói
  OTF/    cài vào máy (macOS, Windows, Linux); nên dùng cho thiết kế và in ấn
  TTF/    TrueType đã hint, cho Windows và phần mềm chỉ nhận TTF
  WOFF2/  cho website
  Bốn độ đậm: Light 300, Regular 400, Medium 500, Bold 700.

Cài đặt
  macOS:   mở các tệp .otf, bấm "Cài đặt phông chữ".
  Windows: chuột phải vào tệp .otf hoặc .ttf, chọn "Install".

Dùng trên web
  Medium dùng cho cả chữ 500 và 600, nên face của nó khai báo dải "500 600". Nếu không, trình
  duyệt sẽ lấy Bold cho chữ 600.

  @font-face { font-family: "KÉT Sans"; src: url(KETSans-Light.woff2) format("woff2"); font-weight: 300; }
  @font-face { font-family: "KÉT Sans"; src: url(KETSans-Regular.woff2) format("woff2"); font-weight: 400; }
  @font-face { font-family: "KÉT Sans"; src: url(KETSans-Medium.woff2) format("woff2"); font-weight: 500 600; }
  @font-face { font-family: "KÉT Sans"; src: url(KETSans-Bold.woff2) format("woff2"); font-weight: 700; }

--------------------------------------------------------------------------------

KÉT Sans {version}

Két Việt's brand typeface: a neutral neo-grotesque for Vietnamese interfaces.
Free to download and use, including commercially and embedded in websites, apps and
documents. The font files may not be modified or redistributed. Full terms in LICENSE.txt.

This is a beta: glyphs, spacing and kerning may change in later releases.

Contents
  OTF/    install on your computer (macOS, Windows, Linux); best for design and print
  TTF/    hinted TrueType, for Windows and software that only takes TTF
  WOFF2/  for websites
  Four weights: Light 300, Regular 400, Medium 500, Bold 700.

Installing
  macOS:   open the .otf files and click "Install Font".
  Windows: right-click the .otf or .ttf files and choose "Install".

On the web
  Medium serves both 500 and 600, so declare its face as "500 600". Otherwise browsers pick
  Bold for 600. Use the @font-face rules above.
