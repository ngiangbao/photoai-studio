<div align="center">

# 📸 PhotoAI Studio

**Chụp ảnh tethering từ máy ảnh qua USB và tự động chỉnh sửa bằng AI — giao diện kiểu app chỉnh ảnh di động, thân thiện cảm ứng**

![Version](https://img.shields.io/badge/version-alpha--002-orange)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini-8E44AD?logo=google)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-red)

[**⬇️ Tải bản cài đặt mới nhất**](../../releases/latest) · [Báo lỗi](../../issues) · [Giới thiệu](#-giới-thiệu)

</div>

---

## 📖 Giới thiệu

**PhotoAI Studio** là ứng dụng desktop cho Windows giúp nhiếp ảnh gia rút ngắn quy trình chụp
& hậu kỳ: kết nối máy ảnh qua dây USB, chụp trực tiếp từ phần mềm, chọn ảnh và phong cách
mong muốn, để AI tự động chỉnh sửa theo đúng phong cách đó — thay vì chỉnh tay từng ảnh trên
Lightroom/Photoshop. Giao diện lấy cảm hứng từ các app chỉnh ảnh di động phổ biến (kiểu
Xingtu/Meitu): thanh điều hướng dưới, thẻ chọn phong cách dạng carousel, thanh kéo so sánh
trước/sau, và các nút/vùng chạm đủ lớn để dùng tốt trên cả màn hình cảm ứng.

> ⚠️ **Đang trong giai đoạn `alpha-002`** — các tính năng cốt lõi đã hoạt động nhưng chưa được
> kiểm thử rộng rãi trên nhiều dòng máy ảnh. Phản hồi & issue luôn được chào đón.

## ✨ Tính năng

**Thư viện** 🖼️ — ảnh mới chụp tự động xuất hiện, chọn nhanh bằng một cú chạm.

**Chỉnh sửa AI** ✨
- 📷 Chụp tethering qua USB qua [digiCamControl](https://www.digicamcontrol.com) (đa số máy ảnh Canon/Nikon/Sony/Pentax)
- 🎨 Carousel chọn 1 trong 5 phong cách dựng sẵn:

  | Phong cách | Mô tả |
  |---|---|
  | Chân dung | Mịn da tự nhiên, nổi bật mắt, làm mờ hậu cảnh nhẹ |
  | Ngoại cảnh | Cân bằng sáng/tối, màu sắc tự nhiên ngoài trời |
  | Phong cảnh | Tăng dynamic range, làm nổi bật bầu trời & chi tiết |
  | Chụp người / đời thường | Màu da chuẩn, ánh sáng đều cho nhiều người |
  | Chụp kỷ yếu | Tông màu tươi sáng, đồng nhất, nổi bật nụ cười |
- 🎚️ Thanh **cường độ hiệu ứng** (0–100%) để pha trộn ảnh AI với ảnh gốc
- 🖱️ **Thanh kéo so sánh** trước/sau ngay trên ảnh (kéo để lộ dần kết quả AI)
- 🤖 Chỉnh sửa bằng AI tạo sinh qua [Gemini API](https://ai.google.dev) (`gemini-2.5-flash-image`), có thể thêm ghi chú tuỳ chỉnh

**Chỉnh tay** 🎚️ — độ sáng, tương phản, bão hoà, độ nét (xem trước trực tiếp) + xoay ảnh 90°, không cần AI.

**Cài đặt** ⚙️ — đổi model AI, đường dẫn digiCamControl, thư mục lưu ảnh.

## 🏗️ Kiến trúc

```
photoai_app/
├── main.py                 # Điểm khởi chạy ứng dụng
├── config.py                # Quản lý cấu hình (API key, đường dẫn, phiên bản)
├── requirements.txt
├── installer.iss            # Script Inno Setup (tự tải & cài digiCamControl)
├── assets/icon.ico           # Icon ứng dụng
├── camera/
│   └── digicam.py            # Wrapper gọi digiCamControl (CameraControlCmd.exe)
├── ai/
│   ├── styles.py              # Định nghĩa 5 phong cách + prompt cho Gemini
│   ├── gemini_editor.py       # Gọi Gemini API chỉnh sửa ảnh
│   └── manual_edit.py         # Chỉnh tay (sáng/tương phản/bão hoà/nét/xoay) + blend AI
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
4. Hoặc tab **Chỉnh tay** → chỉnh sáng/tương phản/bão hoà/nét bằng thanh trượt → **"Lưu ảnh"**.

## 📦 Build installer từ mã nguồn

Mỗi khi tag dạng `v*` được đẩy lên GitHub, workflow **Build & Release Windows Installer**
(`.github/workflows/release.yml`) tự động: build bằng PyInstaller → đóng gói bằng Inno Setup →
đăng `PhotoAIStudio-Setup-*.exe` lên mục **Releases**. Build thủ công:

```bash
pip install pyinstaller
pyinstaller --name "PhotoAI Studio" --windowed --onedir --icon assets/icon.ico main.py
# Sau đó mở installer.iss bằng Inno Setup và Build
```

## 🗺️ Roadmap

- [ ] Hỗ trợ tethering trực tiếp qua SDK riêng (Canon EDSDK, Nikon SDK) ngoài digiCamControl
- [ ] Xử lý hàng loạt nhiều ảnh cùng lúc (batch processing)
- [ ] Tuỳ chỉnh / lưu phong cách của riêng người dùng
- [ ] Bộ icon SVG riêng thay cho emoji, hỗ trợ dark/light theme switch

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
