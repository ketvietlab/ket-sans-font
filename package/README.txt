KÉT Sans {version}

Phông chữ thương hiệu của Két Việt: neo-grotesque trung tính cho giao diện tiếng Việt.
Miễn phí tải và sử dụng, kể cả cho mục đích thương mại và nhúng vào website, ứng dụng, tài
liệu. Không được sửa hay phân phối lại các tệp phông. Điều khoản đầy đủ ở LICENSE.txt.

Bản phát hành 1.0. Chưa kiểm trên Windows/ClearType và Safari/WebKit.
Font Optical còn 5 kết quả FAIL FontBakery liên quan naming/style của family chỉ có opsz;
xem release notes tại https://github.com/ketvietlab/ket-sans-font/releases/tag/v1.0.0.

Trong gói
  OTF/    cài vào máy (macOS, Windows, Linux); nên dùng cho thiết kế và in ấn
  TTF/    TrueType đã hint, cho Windows và phần mềm chỉ nhận TTF
  WOFF2/  font tĩnh có hint cho website
  Optical/  TTF và WOFF2 có trục opsz: spacing tự thu ở cỡ lớn khi ứng dụng hỗ trợ
  Bốn độ đậm: Light 300, Regular 400, Medium 500, Bold 700.

Cài đặt
  macOS:   mở các tệp .otf, bấm "Cài đặt phông chữ".
  Windows: chuột phải vào tệp .otf hoặc .ttf, chọn "Install".

Dùng trên web
  Khuyến nghị bản Optical; không cần thêm letter-spacing âm. Mỗi tệp giữ một độ đậm,
  trục opsz chỉ đổi spacing. Tọa độ 8–16 giữ nhịp Text, 48–72 dùng nhịp Display.
  Font optical chưa có hint căn nét lên lưới; bản tĩnh trong TTF/ và WOFF2/ vẫn có hint.
  Medium dùng cho cả chữ 500 và 600, nên face của nó khai báo dải "500 600". Nếu không, trình
  duyệt sẽ lấy Bold cho chữ 600.

  @font-face { font-family: "KÉT Sans"; src: url(Optical/KETSansOptical-Light.woff2) format("woff2"); font-weight: 300; }
  @font-face { font-family: "KÉT Sans"; src: url(Optical/KETSansOptical-Regular.woff2) format("woff2"); font-weight: 400; }
  @font-face { font-family: "KÉT Sans"; src: url(Optical/KETSansOptical-Medium.woff2) format("woff2"); font-weight: 500 600; }
  @font-face { font-family: "KÉT Sans"; src: url(Optical/KETSansOptical-Bold.woff2) format("woff2"); font-weight: 700; }
  html { font-optical-sizing: auto; }

  font-optical-sizing: none dùng nhịp Text. Ánh xạ cỡ chữ sang opsz do ứng dụng quyết định;
  không giả định giá trị point của trục luôn bằng số px trên mọi nền tảng.

--------------------------------------------------------------------------------

KÉT Sans {version}

Két Việt's brand typeface: a neutral neo-grotesque for Vietnamese interfaces.
Free to download and use, including commercially and embedded in websites, apps and
documents. The font files may not be modified or redistributed. Full terms in LICENSE.txt.

Release 1.0. Windows/ClearType and Safari/WebKit remain unverified.
Optical fonts retain five FontBakery failures concerning naming/style checks for
opsz-only families; see the release notes linked above.

Contents
  OTF/    install on your computer (macOS, Windows, Linux); best for design and print
  TTF/    hinted TrueType, for Windows and software that only takes TTF
  WOFF2/  hinted static fonts for websites
  Optical/  TTF and WOFF2 with an opsz axis for size-dependent spacing
  Four weights: Light 300, Regular 400, Medium 500, Bold 700.

Installing
  macOS:   open the .otf files and click "Install Font".
  Windows: right-click the .otf or .ttf files and choose "Install".

On the web
  Use Optical/ for automatic optical spacing with font-optical-sizing: auto.
  Each file has a fixed weight; only spacing varies. Coordinates 8–16 retain Text
  spacing; 48–72 use Display spacing. Application mapping to opsz may vary.
  Optical fonts have no stem/grid hinting. Hinted static fonts remain in TTF/ and WOFF2/.
  Medium serves both 500 and 600, so declare its face as "500 600". Otherwise browsers pick
  Bold for 600. Use the @font-face rules above.
