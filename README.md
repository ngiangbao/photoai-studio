<div align="center">

# 📸 PhotoAI Studio

**Chụp ảnh tethering từ máy ảnh qua USB và tự động chỉnh sửa bằng AI — giao diện kiểu app chỉnh ảnh di động, thân thiện cảm ứng**

![Version](https://img.shields.io/badge/version-alpha--003-orange)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini-8E44AD?logo=google)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-red)

[**⬇️ Tải bản cài đặt mới nhất**](../../releases/latest) · [Báo lỗi](../../issues) · [Giới thiệu](#-giới-thiệu)

**🇻🇳 Tiếng Việt** | [🇬🇧 English](README.en.md)

</div>

---

## 📖 Giới thiệu

**PhotoAI Studio** là ứng dụng desktop cho Windows giúp nhiếp ảnh gia rút ngắn quy trình chụp
& hậu kỳ: kết nối máy ảnh qua dây USB, chụp trực tiếp từ phần mềm, chọn ảnh và phong cách
mong muốn, để AI tự động chỉnh sửa theo đúng phong cách đó — thay vì chỉnh tay từng ảnh trên
Lightroom/Photoshop. Giao diện lấy cảm hứng từ các app chỉnh ảnh di động phổ biến (kiểu
Xingtu/Meitu): thanh điều hướng dưới, thẻ chọn phong cách dạng carousel, thanh kéo so sánh
trước/sau, và các nút/vùng chạm đủ lớn để dùng tốt trên cả màn hình cảm ứng. Ứng dụng hỗ trợ
song ngữ **Tiếng Việt / English**, chuyển đổi ngay trong app không cần khởi động lại.

> ⚠️ **Đang trong giai đoạn `alpha-003`** — các tính năng cốt lõi đã hoạt động nhưng chưa được
> kiểm thử rộng rãi trên nhiều dòng máy ảnh. Phản hồi & issue luôn được chào đón.
>
> Từ `alpha-003`, một số tính năng được tham khảo từ ứng dụng chỉnh ảnh di động **醒图
> (XingTu/retouchpics.com)**: công cụ 1-chạm, xoá vật thể bằng AI, preset tuỳ chỉnh và
> xử lý hàng loạt — xem chi tiết bên dưới.

## ✨ Tính năng

**Thư viện** 🖼️ — ảnh mới chụp tự động xuất hiện, chọn nhanh bằng một cú chạm. Có thể chuyển
sang **chế độ chọn nhiều** để chọn nhiều ảnh cùng lúc và xử lý hàng loạt.

**Chỉnh sửa AI** ✨
- 📷 Chụp tethering qua USB qua [digiCamControl](https://www.digicamcontrol.com) (đa số máy ảnh Canon/Nikon/Sony/Pentax)
- 🎨 Carousel chọn 1 trong 6 phong cách dựng sẵn:

  | Phong cách | Mô tả |
  |---|---|
  | Chân dung | Mịn da tự nhiên, nổi bật mắt, làm mờ hậu cảnh nhẹ |
  | Ngoại cảnh | Cân bằng sáng/tối, màu sắc tự nhiên ngoài trời |
  | Phong cảnh | Tăng dynamic range, làm nổi bật bầu trời & chi tiết |
  | Chụp người / đời thường | Màu da chuẩn, ánh sáng đều cho nhiều người |
  | Chụp kỷ yếu | Tông màu tươi sáng, đồng nhất, nổi bật nụ cười |
  | 🧹 Xoá vật thể | Xoá người/vật gây xao nhãng ở hậu cảnh, tự phục hồi (inpaint) tự nhiên |
- ⭐ **Preset tuỳ chỉnh** — lưu lại tổ hợp phong cách + cường độ + ghi chú làm preset riêng có
  tên, hiện trong carousel để dùng lại nhanh (nhấn giữ/chuột phải để xoá)
- 🧵 **Xử lý hàng loạt** — chọn nhiều ảnh ở Thư viện rồi áp 1 phong cách/preset cho tất cả, tự
  lưu kết quả, có thanh tiến trình
- 🎚️ Thanh **cường độ hiệu ứng** (0–100%) để pha trộn ảnh AI với ảnh gốc
- 🖱️ **Thanh kéo so sánh** trước/sau ngay trên ảnh (kéo để lộ dần kết quả AI)
- 🤖 Chỉnh sửa bằng AI tạo sinh qua [Gemini API](https://ai.google.dev) (`gemini-2.5-flash-image`), có thể thêm ghi chú tuỳ chỉnh

**Chỉnh tay** 🎚️ — độ sáng, tương phản, bão hoà, độ nét (xem trước trực tiếp) + xoay ảnh 90°,
cộng 2 **công cụ 1-chạm xử lý cục bộ** (không cần AI, chạy ngay lập tức): 🌈 Cân bằng trắng
(gray-world) và ✨ Tự động chỉnh sáng/màu/tương phản.

**Cài đặt** ⚙️ — đổi model AI, đường dẫn digiCamControl, thư mục lưu ảnh, và **ngôn ngữ** (Việt/Anh).

## 🏗️ Kiến trúc

```
photoai_app/
├── main.py                 # Điểm khởi chạy ứng dụng
├── config.py                # Quản lý cấu hình (API key, đường dẫn, phiên bản)
├── requirements.txt
├── installer.iss            # Script Inno Setup (tự tải & cài digiCamControl)
├── assets/icon.ico           # Icon ứng dụng
├── i18n.py                   # Hệ thống dịch song ngữ Việt/Anh nhẹ
├── camera/
│   └── digicam.py            # Wrapper gọi digiCamControl (CameraControlCmd.exe)
├── ai/
│   ├── styles.py              # Định nghĩa 6 phong cách + prompt song ngữ cho Gemini
│   ├── gemini_editor.py       # Gọi Gemini API chỉnh sửa ảnh
│   ├── manual_edit.py         # Chỉnh tay (sáng/tương phản/bão hoà/nét/xoay) + blend AI
│   └── one_tap.py             # Công cụ 1-chạm cục bộ: cân bằng trắng, tự động chỉnh (không cần AI)
└── ui/
    ├── theme.py                # Bảng màu & QSS (giao diện tối, điểm nhấn hồng/tím)
    ├── widgets.py               # Thanh điều hướng dưới, chip phong cách, compare slider
    ├── pages.py                 # 4 trang: Thư viện / Chỉnh AI / Chỉnh tay / Cài đặt
    └── main_window.py           # Cửa sổ chính, điều phối các trang
```

| Thành phần | Công nghệ |
|---|---|
| Giao diện | [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python) |
| Tethering máy ảnh | [digiCamControl](https://www.digicamcontrol.com) (mã nguồn mở) |
| Chỉnh sửa ảnh AI | [Google Gemini API](https://ai.google.dev) (`google-genai`) |
| Xử lý ảnh | [Pillow](https://python-pillow.org) |
| Đóng gói | PyInstaller + Inno Setup, build tự động bằng GitHub Actions |

## ⬇️ Cài đặt nhanh (khuyên dùng)

1. Vào [**Releases**](../../releases/latest) và tải `PhotoAIStudio-Setup-*.exe`.
2. Chạy file, để tuỳ chọn "Tự động tải và cài digiCamControl" được tick sẵn → trình cài đặt
   tự tải và cài digiCamControl, không cần bạn làm thêm bước nào.
3. Mở **PhotoAI Studio** → vào **Cài đặt** nhập Gemini API key (lấy miễn phí tại
   [Google AI Studio](https://ai.google.dev)) — đây là bước duy nhất cần bạn tự làm, vì khoá
   API là riêng tư/tính phí theo tài khoản của bạn nên không thể đóng gói sẵn.

## 📋 Yêu cầu hệ thống

- Windows 10/11
- Gemini API key ([lấy miễn phí tại Google AI Studio](https://ai.google.dev))
- Máy ảnh được digiCamControl hỗ trợ ([danh sách máy ảnh](https://www.digicamcontrol.com/cameras))

## 🧑‍💻 Chạy từ mã nguồn (cho dev)

```bash
git clone https://github.com/ngiangbao/photoai-studio.git
cd photoai-studio
pip install -r requirements.txt
python main.py
```

> ⚠️ Không mở cửa sổ chính digiCamControl khi dùng app này — `CameraControlCmd.exe` chỉ hoạt
> động khi digiCamControl GUI *không* chạy.

## 🖱️ Sử dụng

1. Cắm máy ảnh qua USB, bật máy ảnh.
2. Tab **Thư viện** → **"Chụp ảnh mới"** → chọn ảnh vừa chụp.
3. Tab **Chỉnh AI** → chọn phong cách trên carousel → chỉnh cường độ nếu muốn → **"Áp dụng AI"**
   → kéo thanh so sánh để xem trước/sau → **"Lưu ảnh"**.
4. Hoặc tab **Chỉnh tay** → bấm **"Cân bằng trắng"** / **"Tự động chỉnh"** để sửa nhanh, rồi
   tinh chỉnh thêm bằng thanh trượt → **"Lưu ảnh"**.
5. Muốn dùng lại một tổ hợp phong cách quen thuộc? Chọn phong cách + cường độ + ghi chú ở tab
   **Chỉnh AI** → **"Lưu làm preset"** → đặt tên. Preset xuất hiện trong carousel, chuột phải để xoá.
6. Có nhiều ảnh cùng cần 1 phong cách? Ở tab **Thư viện**, bấm **"Chọn nhiều"** → tick các ảnh →
   **"Xử lý hàng loạt"** (dùng phong cách/preset đang chọn ở tab Chỉnh AI).
7. Đổi ngôn ngữ bất cứ lúc nào ở tab **Cài đặt** → **Ngôn ngữ** (áp dụng ngay, không cần khởi
   động lại).

## 📦 Build installer từ mã nguồn

Mỗi khi tag dạng `v*` được đẩy lên GitHub, workflow **Build & Release Windows Installer**
(`.github/workflows/release.yml`) tự động: build bằng PyInstaller → đóng gói bằng Inno Setup →
đăng `PhotoAIStudio-Setup-*.exe` lên mục **Releases**. Build thủ công:

```bash
pip install pyinstaller
pyinstaller --name "PhotoAI Studio" --windowed --onedir --icon assets/icon.ico main.py
# Sau đó mở installer.iss bằng Inno Setup và Build
```

## 📱 Bản Android

Đang triển khai tại [`android/`](android/) — dùng Kotlin + Jetpack Compose, cùng 5 phong cách
và logic gọi Gemini với bản Windows, nhưng chụp bằng camera của điện thoại (qua CameraX) thay
vì digiCamControl (vốn chỉ chạy trên Windows). Chi tiết kiến trúc và hướng dẫn chạy thử ở
[`android/README.md`](android/README.md).

## 🗺️ Roadmap

- [ ] Hỗ trợ tethering trực tiếp qua SDK riêng (Canon EDSDK, Nikon SDK) ngoài digiCamControl
- [x] Xử lý hàng loạt nhiều ảnh cùng lúc (batch processing)
- [x] Tuỳ chỉnh / lưu phong cách của riêng người dùng (preset)
- [ ] Chỉnh dáng mặt (face reshape/lift) bằng landmark — cần thêm thư viện nhận diện khuôn mặt,
      hiện tại các hiệu ứng khuôn mặt vẫn đi qua AI tạo sinh (phong cách Chân dung) thay vì warp
      mesh chính xác theo điểm mốc
- [ ] Thư viện 1.200+ bộ lọc có thể xếp chồng (filter stack) như bản 醒图 gốc
- [ ] Bộ icon SVG riêng thay cho emoji, hỗ trợ dark/light theme switch
- [ ] Bản Android: nhập ảnh từ thư viện, tethering USB-OTG, bản release ký số (xem roadmap riêng trong `android/README.md`)

## 🤝 Đóng góp

Mọi đóng góp, báo lỗi hay đề xuất tính năng đều được hoan nghênh — hãy mở một
[Issue](../../issues) hoặc gửi Pull Request.

## ☕ Ủng hộ dự án

Nếu bạn thấy **PhotoAI Studio** hữu ích, bạn có thể ủng hộ mình một ly cà phê để duy trì
và phát triển dự án 🙏

<div align="center">
<table>
<tr>
<td align="center" width="50%">
<b>MoMo</b><br/><br/>
<img src="assets/donate-momo.jpg" width="220" alt="QR MoMo ủng hộ dự án PhotoAI Studio"/>
</td>
<td align="center" width="50%">
<b>Ngân hàng (VietQR)</b><br/><br/>
<img src="assets/donate-bank.jpg" width="220" alt="QR ngân hàng VietQR ủng hộ dự án PhotoAI Studio"/>
</td>
</tr>
</table>

Nguyễn Giang Bảo

</div>

## 📄 License

Phát hành theo giấy phép [MIT](LICENSE).

---

<div align="center">

Made with ☕ by [ngiangbao](https://github.com/ngiangbao)

</div>
