package com.ngiangbao.photoaistudio.camera

import android.content.Context
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.ngiangbao.photoaistudio.util.AppError
import com.ngiangbao.photoaistudio.util.AppException
import kotlinx.coroutines.suspendCancellableCoroutine
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * camera/CameraController.kt - Thay the camera/digicam.py.
 *
 * digiCamControl (CameraControlCmd.exe) chup tethering qua USB tu may anh Canon/Nikon/Sony
 * roi, va la cong cu rieng cho Windows - khong co ban tuong duong tren Android, va hau het
 * SDK may anh hang (Canon EDSDK, Nikon SDK, Sony Remote SDK) khong phat hanh cho Android
 * cho ung dung ca nhan/mo nguon mo. Vi vay ban Android dung camera co san cua may
 * (qua CameraX) de "chup tethering" - nguoi dung bam chup ngay trong app, anh luu thang
 * vao thu muc rieng cua app, giu dung luong tron ven workflow chup -> chon -> AI chinh sua.
 *
 * Ket noi may anh roi qua USB-OTG/PTP van la huong mo rong co the lam sau (xem README),
 * nhung doi hoi thu vien PTP/MTP hoac SDK rieng cua tung hang may anh.
 */
class CameraController(private val context: Context) {

    private var imageCapture: ImageCapture? = null
    private var cameraProvider: ProcessCameraProvider? = null

    val captureFolder: File by lazy {
        File(context.getExternalFilesDir(null), "RawCaptures").apply { mkdirs() }
    }

    suspend fun bind(
        lifecycleOwner: LifecycleOwner,
        previewView: PreviewView,
        lensFacing: Int = CameraSelector.LENS_FACING_BACK,
    ) {
        val provider = getCameraProvider()
        val preview = Preview.Builder().build().also {
            it.setSurfaceProvider(previewView.surfaceProvider)
        }
        val capture = ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
            .build()

        val selector = CameraSelector.Builder().requireLensFacing(lensFacing).build()

        provider.unbindAll()
        provider.bindToLifecycle(lifecycleOwner, selector, preview, capture)
        imageCapture = capture
        cameraProvider = provider
    }

    fun unbind() {
        cameraProvider?.unbindAll()
    }

    /** Chup 1 tam anh va luu vao captureFolder. Tra ve duong dan file anh. */
    suspend fun capturePhoto(filename: String? = null): File {
        val capture = imageCapture
            ?: throw AppException(AppError.CameraNotReady)

        val name = filename ?: "IMG_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())}.jpg"
        val targetFile = File(captureFolder, name)
        val outputOptions = ImageCapture.OutputFileOptions.Builder(targetFile).build()

        return suspendCancellableCoroutine { continuation ->
            capture.takePicture(
                outputOptions,
                ContextCompat.getMainExecutor(context),
                object : ImageCapture.OnImageSavedCallback {
                    override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                        continuation.resume(targetFile)
                    }

                    override fun onError(exception: ImageCaptureException) {
                        continuation.resumeWithException(
                            AppException(AppError.CaptureFailed(exception.message ?: exception.toString())),
                        )
                    }
                },
            )
        }
    }

    private suspend fun getCameraProvider(): ProcessCameraProvider =
        suspendCancellableCoroutine { continuation ->
            val future = ProcessCameraProvider.getInstance(context)
            future.addListener(
                {
                    try {
                        continuation.resume(future.get())
                    } catch (exc: Exception) {
                        continuation.resumeWithException(
                            AppException(AppError.CameraInitFailed(exc.message ?: exc.toString())),
                        )
                    }
                },
                ContextCompat.getMainExecutor(context),
            )
        }
}
