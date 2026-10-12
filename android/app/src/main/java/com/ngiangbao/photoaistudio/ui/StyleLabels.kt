package com.ngiangbao.photoaistudio.ui

import androidx.annotation.StringRes
import com.ngiangbao.photoaistudio.R

/**
 * ui/StyleLabels.kt - Anh xa style key -> chuoi hien thi (string resource), de ten phong cach
 * tu dong doi theo ngon ngu may (Viet/Anh) ma khong dong vao prompt gui cho Gemini.
 */
@StringRes
fun styleLabelRes(styleKey: String): Int = when (styleKey) {
    "portrait" -> R.string.style_portrait
    "outdoor" -> R.string.style_outdoor
    "landscape" -> R.string.style_landscape
    "people" -> R.string.style_people
    "graduation" -> R.string.style_graduation
    else -> R.string.style_portrait
}
