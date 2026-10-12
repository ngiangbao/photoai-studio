package com.ngiangbao.photoaistudio.ai

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

/**
 * ai/GeminiEditor.kt - Goi Gemini API de chinh sua anh theo phong cach da chon.
 *
 * Kotlin port of ai/gemini_editor.py. The desktop app uses the `google-genai` Python SDK;
 * there is no equivalent first-party Kotlin SDK bundled here, so this calls the same
 * `generateContent` REST endpoint directly over HTTPS with OkHttp, which keeps behaviour
 * (prompt, image resizing, PROHIBITED_CONTENT handling) identical to the desktop version.
 */
class GeminiEditException(message: String) : Exception(message)

class GeminiEditor(
    private val apiKey: String,
    private val model: String = "gemini-2.5-flash-image",
) {
    init {
        if (apiKey.isBlank()) {
            throw GeminiEditException("Chua co Gemini API key. Vao Cai dat de nhap key.")
        }
    }

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(90, TimeUnit.SECONDS)
        .build()

    /**
     * Gui anh + prompt theo phong cach toi Gemini va tra ve anh da chinh sua (Bitmap).
     */
    suspend fun editImage(
        imagePath: String,
        styleKey: String,
        extraInstruction: String = "",
    ): Bitmap = withContext(Dispatchers.IO) {
        val style = Styles.BY_KEY[styleKey]
            ?: throw GeminiEditException("Khong tim thay phong cach: $styleKey")

        var prompt = style.prompt
        if (extraInstruction.isNotBlank()) {
            prompt += "\n\nYeu cau them tu nguoi dung: ${extraInstruction.trim()}"
        }

        val sourceBitmap = BitmapFactory.decodeFile(imagePath)
            ?: throw GeminiEditException("Khong doc duoc anh: $imagePath")
        val resized = resizeToFit(sourceBitmap, 2048)
        val base64Image = bitmapToBase64Jpeg(resized)

        val requestJson = JSONObject().apply {
            put(
                "contents",
                JSONArray().put(
                    JSONObject().apply {
                        put(
                            "parts",
                            JSONArray()
                                .put(JSONObject().put("text", prompt))
                                .put(
                                    JSONObject().put(
                                        "inline_data",
                                        JSONObject()
                                            .put("mime_type", "image/jpeg")
                                            .put("data", base64Image),
                                    ),
                                ),
                        )
                    },
                ),
            )
        }

        val url = "https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent"
        val request = Request.Builder()
            .url(url)
            .addHeader("x-goog-api-key", apiKey)
            .post(requestJson.toString().toRequestBody("application/json".toMediaType()))
            .build()

        val response = try {
            client.newCall(request).execute()
        } catch (exc: Exception) {
            throw GeminiEditException("Loi khi goi Gemini API: ${exc.message}")
        }

        response.use { resp ->
            val bodyString = resp.body?.string().orEmpty()
            if (!resp.isSuccessful) {
                val detail = try {
                    JSONObject(bodyString).optJSONObject("error")?.optString("message")
                } catch (_: Exception) {
                    null
                } ?: bodyString
                throw GeminiEditException("Loi khi goi Gemini API (HTTP ${resp.code}): $detail")
            }

            val root = JSONObject(bodyString)
            val candidates = root.optJSONArray("candidates")
            if (candidates == null || candidates.length() == 0) {
                throw GeminiEditException("Gemini khong tra ve ket qua nao.")
            }

            val firstCandidate = candidates.getJSONObject(0)
            val finishReason = firstCandidate.optString("finishReason", "")
            if (finishReason == "PROHIBITED_CONTENT") {
                throw GeminiEditException("Noi dung anh bi chan boi bo loc an toan cua Gemini.")
            }

            val content = firstCandidate.optJSONObject("content")
                ?: throw GeminiEditException("Gemini khong tra ve noi dung anh.")
            val parts = content.optJSONArray("parts")
                ?: throw GeminiEditException("Gemini khong tra ve noi dung anh.")

            for (i in 0 until parts.length()) {
                val part = parts.getJSONObject(i)
                val inlineData = part.optJSONObject("inlineData") ?: part.optJSONObject("inline_data")
                val data = inlineData?.optString("data")
                if (!data.isNullOrBlank()) {
                    val bytes = Base64.decode(data, Base64.DEFAULT)
                    return@withContext BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                        ?: throw GeminiEditException("Khong giai ma duoc anh tra ve tu Gemini.")
                }
            }

            throw GeminiEditException("Khong tim thay du lieu anh trong phan hoi cua Gemini.")
        }
    }

    private fun resizeToFit(bitmap: Bitmap, maxDimension: Int): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        if (width <= maxDimension && height <= maxDimension) return bitmap

        val scale = maxDimension.toFloat() / maxOf(width, height)
        val newWidth = (width * scale).toInt().coerceAtLeast(1)
        val newHeight = (height * scale).toInt().coerceAtLeast(1)
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }

    private fun bitmapToBase64Jpeg(bitmap: Bitmap): String {
        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 92, stream)
        return Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP)
    }

    companion object {
        /**
         * Luu ket qua ra file JPEG, tuong duong save_result() trong ban desktop.
         * La ham tinh (khong goi mang) nen khong can khoi tao GeminiEditor voi API key.
         */
        fun saveResult(bitmap: Bitmap, outputPath: String) {
            val outFile = File(outputPath)
            outFile.parentFile?.mkdirs()
            FileOutputStream(outFile).use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 95, out)
            }
        }
    }
}
