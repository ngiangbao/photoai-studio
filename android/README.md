<div align="center">

# 📸 PhotoAI Studio — Android

**Bản Android của PhotoAI Studio: chụp ảnh bằng camera điện thoại, chỉnh sửa bằng AI (Gemini)**

![Platform](https://img.shields.io/badge/platform-Android-3DDC84?logo=android)
![Kotlin](https://img.shields.io/badge/kotlin-2.0-7F52FF?logo=kotlin&logoColor=white)
![UI](https://img.shields.io/badge/UI-Jetpack%20Compose-4285F4?logo=jetpackcompose&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini-8E44AD?logo=google)
![Status](https://img.shields.io/badge/status-alpha-red)

</div>

---

## Khác biệt quan trọng so với bản Windows

Bản desktop dùng **digiCamControl** (`CameraControlCmd.exe`) để chụp tethering qua USB từ máy
ảnh Canon/Nikon/Sony rời. Đây là công cụ **chỉ chạy trên Windows** và không có bản tương đương
trên Android — SDK chính hãng của các hãng máy ảnh (Canon EDSDK, Nikon SDK, Sony Remote SDK)
hầu như không phát hành cho Android cho nhà phát triển cá nhân.

→ Bản Android dùng **camera có sẵn của điện thoại** (qua CameraX) để chụp ảnh trực tiếp trong
app — giữ nguyên workflow "chụp → chọn → chọn phong cách → AI chỉnh sửa → lưu", chỉ khác nguồn
ảnh đầu vào. Việc kết nối máy ảnh rời qua USB-OTG/PTP vẫn khả thi về mặt kỹ thuật nhưng cần một
thư viện PTP/MTP riêng hoặc SDK của từng hãng máy — xem mục Roadmap bên dưới.

Toàn bộ phần còn lại — 5 phong cách chỉnh sửa, prompt gửi cho Gemini, luồng before/after, cấu
hình API key/model — **giống hệt bản desktop** để hai nền tảng cho ra kết quả nhất quán.

## 🏗️ Kiến trúc

```
android/app/src/main/java/com/ngiangbao/photoaistudio/
├── MainActivity.kt          # Diem khoi chay (tuong duong main.py)
├── PhotoAiStudioApp.kt      # Application class
├── ai/
│   ├── EditStyle.kt         # 5 phong cach + prompt (port cua ai/styles.py)
│   └── GeminiEditor.kt      # Goi Gemini REST API (port cua ai/gemini_editor.py)
├── camera/
│   └── CameraController.kt  # CameraX - thay the camera/digicam.py (xem muc tren)
├── data/
│   ├── AppConfig.kt         # Hang so cau hinh (port cua config.py)
│   ├── SettingsRepository.kt# Luu API key/model qua DataStore (thay cho config.json)
│   └── PhotoRepository.kt   # Danh sach anh da chup / duong dan anh da chinh
└── ui/
    ├── AppViewModel.kt      # Dieu phoi camera/AI/settings (logic cua MainWindow)
    ├── HomeScreen.kt        # Xem truoc camera + nut chup + luoi thumbnail
    ├── EditorScreen.kt      # Before/after + chon phong cach + ghi chu + Luu anh
    ├── SettingsScreen.kt    # Nhap Gemini API key / model
    ├── PhotoAiStudioNavHost.kt
    └── theme/                # Material 3 theme
```

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Kotlin 2.0 |
| Giao diện | Jetpack Compose + Material 3 |
| Camera | CameraX (`camera-core`, `camera-camera2`, `camera-view`) |
| Chỉnh sửa ảnh AI | Gọi thẳng REST API của Gemini (`generateContent`) qua OkHttp — không phụ thuộc SDK Android của Google vốn thay đổi nhanh |
| Lưu cấu hình | Jetpack DataStore (Preferences) |
| Tải ảnh thumbnail | Coil |

## 📋 Yêu cầu

- Android Studio (Koala trở lên khuyến nghị)
- JDK 17
- Thiết bị/giả lập Android 8.0 (API 26) trở lên, có camera
- Gemini API key ([lấy miễn phí tại Google AI Studio](https://ai.google.dev))

## 🚀 Chạy thử

1. Mở thư mục `android/` này bằng Android Studio ("Open" → chọn `android/`, không phải thư mục
   gốc repo) — Android Studio sẽ tự tạo Gradle wrapper (`gradlew`) nếu repo chưa có sẵn file
   wrapper jar nhị phân.
2. Để Android Studio tự đồng bộ Gradle; nếu nó gợi ý nâng cấp Android Gradle Plugin/Compose
   Compiler lên bản mới hơn các bản đã khai báo trong `build.gradle.kts`, cứ đồng ý — các
   version trong project này là bản ổn định tại thời điểm viết, không phải bản bắt buộc.
3. Chạy app (▶) trên thiết bị thật hoặc máy ảo có camera.
4. Vào **Cài đặt** (icon bánh răng) → nhập Gemini API key.
5. Về màn hình chính → **Chụp ảnh mới** → chọn ảnh vừa chụp → chọn phong cách → **Chỉnh sửa
   bằng AI** → **Lưu ảnh**.

Ảnh chụp được lưu tại thư mục riêng của app
(`Android/data/com.ngiangbao.photoaistudio/files/RawCaptures`), ảnh đã chỉnh sửa lưu tại
`.../files/Edited` — tương đương `RawCaptures/` và `Edited/` trong `Pictures/PhotoAIStudio/`
của bản desktop.

## 🗺️ Roadmap riêng cho Android

- [ ] Nhập ảnh có sẵn từ thư viện máy (Photo Picker) bên cạnh chụp trực tiếp
- [ ] Kết nối máy ảnh rời qua USB-OTG (PTP/MTP) cho máy hỗ trợ, như một lựa chọn thay thế
      camera điện thoại
- [ ] Chụp hàng loạt / xử lý hàng loạt bằng AI (đồng bộ roadmap với bản desktop)
- [ ] Bản release ký số, đăng lên Google Play / GitHub Releases (`.apk`/`.aab`)

## 🤝 Đóng góp

Theo cùng quy trình với repo chính — mở [Issue](../../issues) hoặc gửi Pull Request.
