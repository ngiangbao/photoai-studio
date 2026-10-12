package com.ngiangbao.photoaistudio.util

/**
 * util/AppError.kt - Loi duoc go o dang co cau truc (khong phai chuoi dung san) de UI co the
 * hien thi bang ca tieng Viet va tieng Anh tuy theo ngon ngu may. Moi truong hop tuong ung
 * voi 1 chuoi trong strings.xml (xem ui/ErrorMessages.kt de map sang stringResource).
 */
sealed class AppError {
    data object MissingApiKey : AppError()
    data object NoPhotoSelected : AppError()
    data object CameraNotReady : AppError()
    data class CameraInitFailed(val detail: String) : AppError()
    data class CaptureFailed(val detail: String) : AppError()
    data class StyleNotFound(val styleKey: String) : AppError()
    data class ImageReadFailed(val path: String) : AppError()
    data class NetworkCallFailed(val detail: String) : AppError()
    data class ApiHttpError(val code: Int, val detail: String) : AppError()
    data object NoCandidatesReturned : AppError()
    data object ProhibitedContent : AppError()
    data object NoContentReturned : AppError()
    data object NoImageInResponse : AppError()
    data object ImageDecodeFailed : AppError()
    data class SaveFailed(val detail: String) : AppError()
    data class Unknown(val detail: String) : AppError()
}

class AppException(val error: AppError) : Exception()

/**
 * Trang thai tam thoi hien thi tren thanh trang thai / snackbar (tuong duong statusBar().showMessage
 * trong ui/main_window.py). Cung duoc go o dang co cau truc vi cung can song ngu.
 */
sealed class AppStatus {
    data class PhotoCaptured(val fileName: String) : AppStatus()
    data object Processing : AppStatus()
    data object ProcessingDone : AppStatus()
    data class PhotoSaved(val path: String) : AppStatus()
}
