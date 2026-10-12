package com.ngiangbao.photoaistudio.data

/**
 * data/AppConfig.kt - Cau hinh chung cho ung dung.
 *
 * Kotlin port of config.py's DEFAULT_CONFIG + the constants in that file. Values are
 * persisted through SettingsRepository (Preferences DataStore) instead of a JSON file,
 * which is the idiomatic equivalent on Android.
 */
object AppConfig {
    const val APP_NAME = "PhotoAI Studio"
    const val APP_VERSION = "alpha-001"
    const val DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-image"
}

data class AppSettings(
    val geminiApiKey: String = "",
    val geminiModel: String = AppConfig.DEFAULT_GEMINI_MODEL,
)
