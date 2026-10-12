package com.ngiangbao.photoaistudio.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/**
 * data/PhotoRepository.kt - Danh sach anh da chup/nhap, tuong duong _refresh_photo_list()
 * trong ui/main_window.py ben desktop (noi dung do QFileSystemWatcher theo doi thu muc chup).
 */
class PhotoRepository(context: Context) {

    val captureFolder: File = File(context.getExternalFilesDir(null), "RawCaptures").apply { mkdirs() }
    val outputFolder: File = File(context.getExternalFilesDir(null), "Edited").apply { mkdirs() }

    suspend fun listCapturedPhotos(): List<File> = withContext(Dispatchers.IO) {
        captureFolder.listFiles { file ->
            file.isFile && file.extension.lowercase() in setOf("jpg", "jpeg", "png")
        }
            ?.sortedByDescending { it.lastModified() }
            ?: emptyList()
    }

    fun outputFileFor(sourcePath: String, styleKey: String): File {
        val stem = File(sourcePath).nameWithoutExtension
        return File(outputFolder, "${stem}_${styleKey}.jpg")
    }
}
