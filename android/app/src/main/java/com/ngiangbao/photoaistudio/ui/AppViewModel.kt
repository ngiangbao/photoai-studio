package com.ngiangbao.photoaistudio.ui

import android.app.Application
import android.graphics.Bitmap
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ngiangbao.photoaistudio.ai.GeminiEditException
import com.ngiangbao.photoaistudio.ai.GeminiEditor
import com.ngiangbao.photoaistudio.ai.Styles
import com.ngiangbao.photoaistudio.camera.CameraController
import com.ngiangbao.photoaistudio.camera.CameraControllerException
import com.ngiangbao.photoaistudio.data.AppSettings
import com.ngiangbao.photoaistudio.data.PhotoRepository
import com.ngiangbao.photoaistudio.data.SettingsRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

data class UiState(
    val photos: List<File> = emptyList(),
    val selectedPhotoPath: String? = null,
    val selectedStyleKey: String = Styles.ALL.first().key,
    val extraNote: String = "",
    val editedBitmap: Bitmap? = null,
    val isCapturing: Boolean = false,
    val isProcessing: Boolean = false,
    val statusMessage: String? = null,
    val errorMessage: String? = null,
    val settings: AppSettings = AppSettings(),
    val lastSavedPath: String? = null,
)

/**
 * ui/AppViewModel.kt - Dieu phoi camera / AI / settings cho UI, tuong duong phan logic
 * nam trong MainWindow cua ui/main_window.py (ben desktop UI va logic gop chung trong 1 lop).
 */
class AppViewModel(application: Application) : AndroidViewModel(application) {

    val cameraController = CameraController(application)
    private val photoRepository = PhotoRepository(application)
    private val settingsRepository = SettingsRepository(application)

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val settings = settingsRepository.load()
            _uiState.update { it.copy(settings = settings) }
        }
        refreshPhotos()
    }

    fun refreshPhotos() {
        viewModelScope.launch {
            val photos = photoRepository.listCapturedPhotos()
            _uiState.update { it.copy(photos = photos) }
        }
    }

    fun capturePhoto() {
        viewModelScope.launch {
            _uiState.update { it.copy(isCapturing = true, errorMessage = null) }
            try {
                val file = cameraController.capturePhoto()
                _uiState.update {
                    it.copy(isCapturing = false, statusMessage = "Da chup: ${file.name}")
                }
                refreshPhotos()
                selectPhoto(file.absolutePath)
            } catch (exc: CameraControllerException) {
                _uiState.update { it.copy(isCapturing = false, errorMessage = exc.message) }
            }
        }
    }

    fun selectPhoto(path: String) {
        _uiState.update {
            it.copy(
                selectedPhotoPath = path,
                editedBitmap = null,
                statusMessage = null,
            )
        }
    }

    fun selectStyle(styleKey: String) {
        _uiState.update { it.copy(selectedStyleKey = styleKey) }
    }

    fun updateExtraNote(note: String) {
        _uiState.update { it.copy(extraNote = note) }
    }

    fun processWithAi() {
        val state = _uiState.value
        val photoPath = state.selectedPhotoPath
        if (photoPath == null) {
            _uiState.update { it.copy(errorMessage = "Hay chon mot anh truoc.") }
            return
        }
        if (state.settings.geminiApiKey.isBlank()) {
            _uiState.update { it.copy(errorMessage = "Hay vao Cai dat de nhap Gemini API key.") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isProcessing = true, errorMessage = null, statusMessage = "AI dang xu ly anh, vui long cho...") }
            try {
                val editor = GeminiEditor(state.settings.geminiApiKey, state.settings.geminiModel)
                val result = editor.editImage(photoPath, state.selectedStyleKey, state.extraNote)
                _uiState.update {
                    it.copy(isProcessing = false, editedBitmap = result, statusMessage = "Xu ly xong.")
                }
            } catch (exc: GeminiEditException) {
                _uiState.update { it.copy(isProcessing = false, statusMessage = null, errorMessage = exc.message) }
            } catch (exc: Exception) {
                _uiState.update {
                    it.copy(isProcessing = false, statusMessage = null, errorMessage = "Loi khong xac dinh: ${exc.message}")
                }
            }
        }
    }

    fun saveEditedPhoto() {
        val state = _uiState.value
        val bitmap = state.editedBitmap
        val sourcePath = state.selectedPhotoPath
        if (bitmap == null || sourcePath == null) return

        viewModelScope.launch {
            val outFile = photoRepository.outputFileFor(sourcePath, state.selectedStyleKey)
            try {
                withContext(Dispatchers.IO) { GeminiEditor.saveResult(bitmap, outFile.absolutePath) }
                _uiState.update { it.copy(lastSavedPath = outFile.absolutePath, statusMessage = "Da luu anh tai: ${outFile.absolutePath}") }
            } catch (exc: Exception) {
                _uiState.update { it.copy(errorMessage = "Khong luu duoc anh: ${exc.message}") }
            }
        }
    }

    fun updateSettings(newSettings: AppSettings) {
        viewModelScope.launch {
            settingsRepository.save(newSettings)
            _uiState.update { it.copy(settings = newSettings) }
        }
    }

    fun clearMessages() {
        _uiState.update { it.copy(errorMessage = null, statusMessage = null) }
    }
}
