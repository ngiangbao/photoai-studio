package com.ngiangbao.photoaistudio.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "photoai_studio_settings")

/**
 * data/SettingsRepository.kt - Quan ly cau hinh (API key, model).
 *
 * Kotlin port of config.py's load_config()/save_config(), backed by Jetpack Preferences
 * DataStore (the Android-idiomatic replacement for the desktop app's
 * %APPDATA%/PhotoAIStudio/config.json file). capture/output folders are not stored here:
 * on Android those live under MediaStore/app-specific storage, handled by CameraController
 * and the gallery, rather than a user-editable path like on Windows.
 */
class SettingsRepository(private val context: Context) {

    private object Keys {
        val GEMINI_API_KEY = stringPreferencesKey("gemini_api_key")
        val GEMINI_MODEL = stringPreferencesKey("gemini_model")
    }

    val settingsFlow: Flow<AppSettings> = context.dataStore.data.map { prefs ->
        AppSettings(
            geminiApiKey = prefs[Keys.GEMINI_API_KEY] ?: "",
            geminiModel = prefs[Keys.GEMINI_MODEL] ?: AppConfig.DEFAULT_GEMINI_MODEL,
        )
    }

    suspend fun load(): AppSettings = settingsFlow.first()

    suspend fun save(settings: AppSettings) {
        context.dataStore.edit { prefs ->
            prefs[Keys.GEMINI_API_KEY] = settings.geminiApiKey
            prefs[Keys.GEMINI_MODEL] = settings.geminiModel.ifBlank { AppConfig.DEFAULT_GEMINI_MODEL }
        }
    }
}
