package com.ngiangbao.photoaistudio.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import com.ngiangbao.photoaistudio.R
import com.ngiangbao.photoaistudio.util.AppError
import com.ngiangbao.photoaistudio.util.AppStatus

/**
 * ui/ErrorMessages.kt - Chuyen AppError/AppStatus (du lieu co cau truc) thanh chuoi hien thi
 * theo ngon ngu hien tai cua may (Viet/Anh), doc tu strings.xml.
 */
@Composable
fun AppError.localizedMessage(): String = when (this) {
    AppError.MissingApiKey -> stringResource(R.string.error_missing_api_key)
    AppError.NoPhotoSelected -> stringResource(R.string.error_no_photo_selected)
    AppError.CameraNotReady -> stringResource(R.string.error_camera_not_ready)
    is AppError.CameraInitFailed -> stringResource(R.string.error_camera_init_failed, detail)
    is AppError.CaptureFailed -> stringResource(R.string.error_capture_failed, detail)
    is AppError.StyleNotFound -> stringResource(R.string.error_style_not_found, styleKey)
    is AppError.ImageReadFailed -> stringResource(R.string.error_image_read_failed, path)
    is AppError.NetworkCallFailed -> stringResource(R.string.error_network_call_failed, detail)
    is AppError.ApiHttpError -> stringResource(R.string.error_api_http_error, code, detail)
    AppError.NoCandidatesReturned -> stringResource(R.string.error_no_candidates)
    AppError.ProhibitedContent -> stringResource(R.string.error_prohibited_content)
    AppError.NoContentReturned -> stringResource(R.string.error_no_content)
    AppError.NoImageInResponse -> stringResource(R.string.error_no_image_in_response)
    AppError.ImageDecodeFailed -> stringResource(R.string.error_image_decode_failed)
    is AppError.SaveFailed -> stringResource(R.string.error_save_failed, detail)
    is AppError.Unknown -> stringResource(R.string.error_unknown, detail)
}

@Composable
fun AppStatus.localizedMessage(): String = when (this) {
    is AppStatus.PhotoCaptured -> stringResource(R.string.status_photo_captured, fileName)
    AppStatus.Processing -> stringResource(R.string.status_processing)
    AppStatus.ProcessingDone -> stringResource(R.string.status_processing_done)
    is AppStatus.PhotoSaved -> stringResource(R.string.status_photo_saved, path)
}
