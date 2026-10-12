<div align="center">

# 📸 PhotoAI Studio

**Chụp ảnh tethering từ máy ảnh qua USB và tự động chỉnh sửa bằng AI**

![Version](https://img.shields.io/badge/version-alpha--001-orange)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini-8E44AD?logo=google)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-red)

</div>

---

## Giới thiệu

**PhotoAI Studio** là ứng dụng desktop cho Windows giúp nhiếp ảnh gia rút ngắn quy trình chụp
& hậu kỳ: kết nối máy ảnh qua dây USB, chụp trực tiếp từ phần mềm, chọn ảnh và phong cách
mong muốn, để AI tự động chỉnh sửa theo đúng phong cách đó — thay vì chỉnh tay từng ảnh trên
Lightroom/Photoshop.

> ⚠️ **Đang trong giai đoạn `alpha-001`** — các tính năng cốt lõi đã hoạt động nhưng chưa được
> kiểm thử rộng rãi trên nhiều dòng máy ảnh. Phản hồi & issue luôn được chào đón.

## ✨ Tính năng

- 📷 **Chụp tethering qua USB** — kích hoạt máy ảnh chụp trực tiếp từ ứng dụng thông qua
  [digiCamControl](https://www.digicamcontrol.com), hỗ trợ đa số máy ảnh Canon/Nikon/Sony/Pentax.
- 🖼️ **Thư viện ảnh trực quan** — ảnh mới chụp tự động xuất hiện trong danh sách, chọn nhanh
  bằng một cú click.
- 🎨 **5 phong cách chỉnh sửa dựng sẵn**:
  | Phong cách | Mô tả |
  |---|---|
  | Chân dung | Mịn da tự nhiên, nổi bật mắt, làm mờ hậu cảnh nhẹ |
  | Ngoại cảnh | Cân bằng sáng/tối, màu sắc tự nhiên ngoài trời |
  | Phong cảnh | Tăng dynamic range, làm nổi bật bầu trời & chi tiết |
  | Chụp người / đời thường | Màu da chuẩn, ánh sáng đều cho nhiều người |
  | Chụp kỷ yếu | Tông màu tươi sáng, đồng nhất, nổi bật nụ cười |
- 🤖 **Chỉnh sửa bằng AI tạo sinh** qua [Gemini API](https://ai.google.dev) (`gemini-2.5-flash-image`),
  có thể thêm ghi chú tuỳ chỉnh cho từng ảnh.
- 👁️ **Xem trước before/after** ngay trong ứng dụng trước khi lưu.
- ⚙️ **Cấu hình linh hoạt** — đổi model AI, đường dẫn digiCamControl, thư mục lưu ảnh ngay
  trong giao diện Cài đặt.

## 🏗️ Kiến trúc

```
photoai_app/
├── main.py                # Điểm khởi chạy ứng dụng
├── config.py               # Quản lý cấu hình (API key, đường dẫn, phiên bản)
├── requirements.txt
├── camera/
│   └── digicam.py          # Wrapper gọi digiCamControl (CameraControlCmd.exe)
├── ai/
│   ├── styles.py            # Định nghĩa 5 phong cách + prompt cho Gemini
│   └── gemini_editor.py     # Gọi Gemini API chỉnh sửa ảnh
└── ui/
    └── main_window.py       # Giao diện chính (PySide6)
```

| Thành phần | Công nghệ |
|---|---|
| Giao diện | [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python) |
| Tethering máy ảnh | [digiCamControl](https://www.digicamcontrol.com) (mã nguồn mở) |
| Chỉnh sửa ảnh AI | [Google Gemini API](https://ai.google.dev) (`google-genai`) |
| Xử lý ảnh | [Pillow](https://python-pillow.org) |
| Đóng gói | PyInstaller + Inno Setup |

## 📋 Yêu cầu hệ thống

- Windows 10/11
- Python 3.10 trở lên
- [digiCamControl](https://www.digicamcontrol.com/doc/basics/download) đã cài đặt
- Gemini API key ([lấy miễn phí tại Google AI Studio](https://ai.google.dev))
- Máy ảnh được digiCamControl hỗ trợ ([danh sách máy ảnh](https://www.digicamcontrol.com/cameras))

## 🚀 Cài đặt

```bash
git clone https://github.com/ngiangbao/photoai-studio.git
cd photoai-studio
pip install -r requirements.txt
python main.py
```

Vào **Cài đặt** trong ứng dụng để nhập Gemini API key và kiểm tra đường dẫn
`CameraControlCmd.exe` (mặc định `C:\Program Files\digiCamControl\CameraControlCmd.exe`).

> ⚠️ Không mở cửa sổ chính digiCamControl khi dùng app này — `CameraControlCmd.exe` chỉ hoạt
> động khi digiCamControl GUI *không* chạy.

## 🖱️ Sử dụng

1. Cắm máy ảnh qua USB, bật máy ảnh.
2. Bấm **"Chụp ảnh mới"** → ảnh xuất hiện trong danh sách bên trái.
3. Chọn một ảnh → chọn **phong cách** → (tuỳ chọn) thêm ghi chú.
4. Bấm **"Chỉnh sửa bằng AI"** → xem kết quả ở khung bên phải.
5. Bấm **"Lưu ảnh"** để xuất ảnh đã chỉnh sửa.

## 📦 Đóng gói thành app cài đặt (.exe)

```bash
pip install pyinstaller
pyinstaller --name "PhotoAI Studio" --windowed --onedir main.py
```

Sau đó dùng [Inno Setup](https://jrsoftware.org/isinfo.php) để đóng gói thư mục
`dist/PhotoAI Studio/` thành một trình cài đặt `setup.exe`.

## 🗺️ Roadmap

- [ ] Hỗ trợ tethering trực tiếp qua SDK riêng (Canon EDSDK, Nikon SDK) ngoài digiCamControl
- [ ] Xử lý hàng loạt nhiều ảnh cùng lúc (batch processing)
- [ ] Tuỳ chỉnh / lưu phong cách của riêng người dùng
- [ ] Trình cài đặt `.exe` chính thức (GitHub Releases)

## 🤝 Đóng góp

Mọi đóng góp, báo lỗi hay đề xuất tính năng đều được hoan nghênh — hãy mở một
[Issue](../../issues) hoặc gửi Pull Request.

## 📄 License

Phát hành theo giấy phép [MIT](LICENSE).

---

<div align="center">

Made with ☕ by [ngiangbao](https://github.com/ngiangbao)

</div>
